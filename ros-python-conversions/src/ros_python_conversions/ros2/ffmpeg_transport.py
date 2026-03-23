"""Decode ffmpeg_image_transport ``FFMPEGPacket`` streams (e.g. OAK low-bandwidth)."""

from __future__ import annotations

import io
import re
import subprocess
from typing import Any, List, Optional, Tuple

import numpy as np

_FFMPEG_MSG = "ffmpeg_image_transport_msgs/msg/FFMPEGPacket"


def is_ffmpeg_packet_msgtype(msgtype: str) -> bool:
    """Return True if ``msgtype`` is ``FFMPEGPacket``.

    Parameters
    ----------
    msgtype : str
        ROS 2 message type string from the bag connection.

    Returns
    -------
    bool
        True when the topic carries ``FFMPEGPacket`` messages.
    """
    return msgtype == _FFMPEG_MSG or msgtype.endswith("/FFMPEGPacket")


def _as_str(encoding: Any) -> str:
    if encoding is None:
        return ""
    if isinstance(encoding, bytes):
        return encoding.decode("utf-8", errors="replace").strip("\x00")
    return str(encoding).strip("\x00")


def _msg_data_bytes(data: Any) -> bytes:
    """Convert ``FFMPEGPacket.data`` to bytes (rosbags often uses ``ndarray``).

    Parameters
    ----------
    data : Any
        Payload: ``None``, ``bytes``, ``memoryview``, ``ndarray``, or sequence.

    Returns
    -------
    bytes
        Raw bytes; empty if missing or length zero.
    """
    if data is None:
        return b""
    if isinstance(data, np.ndarray):
        if data.size == 0:
            return b""
        return np.ascontiguousarray(data, dtype=np.uint8).tobytes()
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    return bytes(data)


def _starts_annex_b(data: bytes) -> bool:
    return (
        len(data) >= 4
        and data[0:4] == b"\x00\x00\x00\x01"
        or len(data) >= 3
        and data[0:3] == b"\x00\x00\x01"
    )


def _length_prefixed_to_annex_b(data: bytes, big_endian: bool = True) -> bytes:
    """Turn 4-byte length + NAL chunks into Annex B (start codes).

    Parameters
    ----------
    data : bytes
        Possibly AVCC / length-prefixed NAL stream.
    big_endian : bool
        If False, use little-endian lengths (some embedded stacks).

    Returns
    -------
    bytes
        Annex B stream, or ``data`` if parsing fails or already Annex B.
    """
    if not data or _starts_annex_b(data):
        return data
    order = "big" if big_endian else "little"
    out = bytearray()
    i = 0
    nmax = len(data)
    while i + 4 <= nmax:
        n = int.from_bytes(data[i : i + 4], order)
        i += 4
        if n < 1 or n > nmax - i or n > 8_000_000:
            return data if not out else bytes(out)
        out.extend(b"\x00\x00\x00\x01")
        out.extend(data[i : i + n])
        i += n
    return bytes(out) if out else data


def _ensure_annex_b_fragment(data: bytes) -> bytes:
    """One bag message payload as Annex B fragment(s).

    Parameters
    ----------
    data : bytes
        Single ``FFMPEGPacket.data``.

    Returns
    -------
    bytes
        Annex B–safe chunk to concatenate.
    """
    if not data:
        return b""
    if _starts_annex_b(data):
        return data
    conv_be = _length_prefixed_to_annex_b(data, True)
    if conv_be != data and _starts_annex_b(conv_be):
        return conv_be
    conv_le = _length_prefixed_to_annex_b(data, False)
    if conv_le != data and _starts_annex_b(conv_le):
        return conv_le
    return b"\x00\x00\x00\x01" + data


def _encoding_to_codec_name(encoding: str) -> str:
    """Map ``FFMPEGPacket.encoding`` to elementary stream type.

    Parameters
    ----------
    encoding : str
        Value from the message ``encoding`` field.

    Returns
    -------
    str
        ``h264`` or ``hevc`` for demuxer format names.
    """
    e = encoding.lower()
    if any(x in e for x in ("hevc", "h265", "hvc1", "hev1")):
        return "hevc"
    if any(x in e for x in ("h264", "avc1", "x264", "264")):
        return "h264"
    m = re.search(r"(h264|hevc|h265)", e)
    if m:
        return "hevc" if "hev" in m.group(1) or "265" in m.group(1) else "h264"
    return "h264"


def _demux_all_bgr(raw: bytes, codec_name: str) -> List[np.ndarray]:
    """Decode concatenated elementary stream to BGR frames.

    Parameters
    ----------
    raw : bytes
        Concatenated packet payloads.
    codec_name : str
        ``h264`` or ``hevc``.

    Returns
    -------
    list of ndarray
        BGR uint8 frames.

    Raises
    ------
    av.AVError
        If demux/decode fails.
    """
    import av

    fmt = "h264" if codec_name == "h264" else "hevc"
    container = av.open(io.BytesIO(raw), format=fmt, mode="r")
    try:
        out: List[np.ndarray] = []
        for packet in container.demux(video=0):
            for frame in packet.decode():
                out.append(frame.to_ndarray(format="bgr24"))
        return out
    finally:
        container.close()


def _align_frame_list_to_msg_count(frames: List[np.ndarray], n: int) -> List[np.ndarray]:
    """Stretch or shrink decoded frame list to match message count.

    Parameters
    ----------
    frames : list of ndarray
        Decoded BGR frames.
    n : int
        Target length (number of bag messages).

    Returns
    -------
    list of ndarray
        Length ``n``.
    """
    if not frames:
        raise ValueError("Demux produced no frames")
    if len(frames) == n:
        return frames
    if len(frames) > n:
        return list(frames[:n])
    pad = frames[-1]
    return list(frames) + [pad.copy() for _ in range(n - len(frames))]


def _try_demux(raw: bytes, codec_name: str) -> Optional[List[np.ndarray]]:
    if len(raw) < 8:
        return None
    try:
        frames = _demux_all_bgr(raw, codec_name)
        return frames if frames else None
    except Exception:
        return None


def _stream_candidates(msgs: List[Any]) -> List[Tuple[str, bytes]]:
    """Build raw bytestream variants to try with demuxers.

    Parameters
    ----------
    msgs : list
        FFMPEGPacket messages in order.

    Returns
    -------
    list of tuple
        (label, bytes) for decoding attempts.
    """
    chunks = [_msg_data_bytes(m.data) for m in msgs]
    plain = b"".join(chunks)
    per_annex = b"".join(_ensure_annex_b_fragment(c) for c in chunks if c)
    whole_be = _length_prefixed_to_annex_b(plain, True)
    whole_le = _length_prefixed_to_annex_b(plain, False)
    out: List[Tuple[str, bytes]] = []
    for label, buf in (
        ("plain_concat", plain),
        ("per_msg_annex", per_annex),
        ("whole_avcc_be", whole_be),
        ("whole_avcc_le", whole_le),
    ):
        if len(buf) >= 8:
            out.append((label, buf))
    return out


def _decode_ffmpeg_cli(
    raw: bytes, width: int, height: int, codec_fmt: str
) -> Optional[List[np.ndarray]]:
    """Decode via ``ffmpeg`` CLI (tolerates some bitstreams PyAV rejects).

    Parameters
    ----------
    raw : bytes
        Elementary stream.
    width : int
        Frame width from message (must be > 0).
    height : int
        Frame height from message (must be > 0).
    codec_fmt : str
        ``h264`` or ``hevc`` for ``-f``.

    Returns
    -------
    list of ndarray or None
        BGR frames if successful.
    """
    if width <= 0 or height <= 0 or not raw:
        return None
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                codec_fmt,
                "-i",
                "pipe:0",
                "-pix_fmt",
                "bgr24",
                "-f",
                "rawvideo",
                "pipe:1",
            ],
            input=raw,
            capture_output=True,
            timeout=600,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    fs = width * height * 3
    data = proc.stdout
    frames: List[np.ndarray] = []
    for i in range(0, len(data) // fs * fs, fs):
        frames.append(
            np.frombuffer(data[i : i + fs], dtype=np.uint8)
            .reshape((height, width, 3))
            .copy()
        )
    return frames if frames else None


def ffmpeg_packets_to_bgr_frames(msgs: List[Any]) -> List[np.ndarray]:
    """Decode a chronological list of ``FFMPEGPacket`` messages to BGR images.

    Tries concatenated elementary streams (plain, Annex B per message, AVCC
    converted), both H.264 and HEVC, then optional ``ffmpeg`` CLI if width and
    height are set on the first message.

    Parameters
    ----------
    msgs : list of Any
        Deserialized ``FFMPEGPacket`` messages in bag order.

    Returns
    -------
    list of ndarray
        uint8 arrays shaped ``(H, W, 3)`` BGR, length ``len(msgs)``.

    Raises
    ------
    ImportError
        If PyAV (``av``) is not installed.
    ValueError
        If ``msgs`` is empty or decoding fails.
    """
    try:
        import av  # noqa: F401
    except ImportError as err:
        raise ImportError(
            "Decoding FFMPEGPacket requires PyAV. Install with: pip install av"
        ) from err

    if not msgs:
        raise ValueError("No FFMPEGPacket messages to decode")

    enc_codec = _encoding_to_codec_name(_as_str(msgs[0].encoding))
    alt = "hevc" if enc_codec == "h264" else "h264"
    w, h = int(msgs[0].width), int(msgs[0].height)
    n = len(msgs)

    last_err: Optional[BaseException] = None
    for codec in (enc_codec, alt):
        for _label, buf in _stream_candidates(msgs):
            got = _try_demux(buf, codec)
            if got:
                try:
                    return _align_frame_list_to_msg_count(got, n)
                except ValueError:
                    pass
            if w > 0 and h > 0:
                cli = _decode_ffmpeg_cli(buf, w, h, codec)
                if cli:
                    try:
                        return _align_frame_list_to_msg_count(cli, n)
                    except ValueError:
                        pass

    try:
        plain = b"".join(_msg_data_bytes(m.data) for m in msgs)
        _demux_all_bgr(plain, enc_codec)
    except Exception as e:
        last_err = e

    raise ValueError(
        "Could not decode FFMPEGPacket stream (tried h264/hevc, Annex B / "
        "length-prefixed layouts, and ffmpeg CLI when W/H are set). "
        f"First message encoding={_as_str(msgs[0].encoding)!r}. "
        f"Last error: {last_err!r}"
    )
