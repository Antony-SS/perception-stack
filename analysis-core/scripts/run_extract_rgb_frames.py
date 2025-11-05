from analysis_core.extract_rgb_frames import extract_rgb_frames
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag_path", type=str, required=True)
    parser.add_argument("--image_topic", type=str, required=False, default="/camera/color/image_raw")
    parser.add_argument("--output_dir", type=str, required=False)
    parser.add_argument("--overlay_timestamps", action="store_true", required=False)
    parser.add_argument("--overlay_pose", action="store_true", required=False)
    parser.add_argument("--pose_topic", type=str, required=False, default="/pose")
    parser.add_argument("--use_header_timestamps", type=bool, required=False, default=True)
    return parser.parse_args()

def main():
    args = parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join("analysis_outputs", os.path.basename(args.bag_path), "rgb_frames")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print(f"Extracting RGB frames from bag {args.bag_path} and topic {args.image_topic} to {args.output_dir}")

    extract_rgb_frames(
        args.bag_path,
        args.image_topic,
        args.output_dir,
        args.overlay_timestamps,
        args.overlay_pose,
        args.pose_topic,
        args.use_header_timestamps
    )

if __name__ == "__main__":
    main()