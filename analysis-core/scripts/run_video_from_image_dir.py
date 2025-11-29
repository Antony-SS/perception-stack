import os
import ffmpeg
import argparse
import glob
from typing import Optional

IMAGE_FILE_TYPES = ["png", "jpg", "jpeg"]


def video_from_image_dir(image_dir : str, output_video_path : str, fps : int = 30, image_file_type : str = "png", frame_step : int = 1) -> None:
    """
    Create a video from a directory of images, assumed to be in the format of 000000.png, 000001.png, etc.

    Parameters
    ----------
    image_dir : str
        Path to the directory of images
    output_video_path : str
        Path to the output video
    fps : int
        Frames per second
    image_file_type : str
        Type of image file to use
    frame_step : int
        The increment between frame numbers (e.g., 5 if images are 000000.png, 000005.png, 000010.png)
    """

    if image_file_type not in IMAGE_FILE_TYPES:
        raise ValueError(f"Invalid image file type: {image_file_type}. Must be one of {IMAGE_FILE_TYPES}")

    # If frame_step is 1, use the simple pattern (sequential numbering)
    if frame_step == 1:
        pattern = os.path.join(image_dir, f"%06d.{image_file_type}")
        print(f"Creating video from {pattern} to {output_video_path} at {fps} fps")
        try:
            ffmpeg.input(pattern).output(output_video_path, vf=f"fps={fps}", pix_fmt="yuv420p").run()
        except Exception as e:
            raise ValueError(f"Failed to create video: {e}")
    else:
        # For non-sequential numbering, use glob to find all matching files
        pattern = os.path.join(image_dir, f"*.{image_file_type}")
        image_files = sorted(glob.glob(pattern))
        
        if not image_files:
            raise ValueError(f"No image files found matching pattern {pattern}")
        
        print(f"Creating video from {len(image_files)} images in {image_dir} to {output_video_path} at {fps} fps")
        
        # Create a temporary concat file listing all images
        concat_file = os.path.join(image_dir, "ffmpeg_concat.txt")
        try:
            with open(concat_file, 'w') as f:
                for image_file in image_files:
                    f.write(f"file '{os.path.abspath(image_file)}'\n")
                    f.write(f"duration 1\n")
                # Repeat last frame to ensure proper duration
                f.write(f"file '{os.path.abspath(image_files[-1])}'\n")
            
            # Use concat demuxer with fps filter
            try:
                ffmpeg.input(concat_file, format='concat', safe=0).output(
                    output_video_path, 
                    vf=f"fps={fps}", 
                    pix_fmt="yuv420p"
                ).run(overwrite_output=True)
            except Exception as e:
                raise ValueError(f"Failed to create video: {e}")
            finally:
                # Clean up concat file
                if os.path.exists(concat_file):
                    os.remove(concat_file)
        except Exception as e:
            raise ValueError(f"Failed to create concat file: {e}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", type=str, required=True)
    parser.add_argument("--output_video_path", type=str, required=False, default=os.path.join("analysis_outputs", "video.mp4"))
    parser.add_argument("--fps", type=int, required=False, default=30)
    parser.add_argument("--image_file_type", type=str, required=False, default="png")
    parser.add_argument("--frame_step", type=int, required=False, default=1, help="Increment between frame numbers (e.g., 5 for 000000.png, 000005.png, 000010.png)")
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.image_dir):
        raise ValueError(f"Image directory {args.image_dir} does not exist")

    if not os.path.exists(os.path.dirname(args.output_video_path)):
        raise ValueError(f"Output video directory {os.path.dirname(args.output_video_path)} does not exist")

    print(f"Creating video from {args.image_dir} to {args.output_video_path} at {args.fps} fps")

    video_from_image_dir(args.image_dir, args.output_video_path, args.fps, args.image_file_type, args.frame_step)

if __name__ == "__main__":
    main()