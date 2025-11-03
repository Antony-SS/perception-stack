from analysis_core.extract_rgb_frames import extract_rgb_frames
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag_path", type=str, required=True)
    parser.add_argument("--image_topic", type=str, required=False, default="/camera/color/image_raw")
    parser.add_argument("--output_dir", type=str, required=False)
    return parser.parse_args()

def main():
    args = parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join("analysis_outputs", os.path.basename(args.bag_path), "rgb_frames")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    extract_rgb_frames(args.bag_path, args.image_topic, args.output_dir)
    print(f"Extracted RGB frames from bag {args.bag_path} and topic {args.image_topic} to {args.output_dir}")

if __name__ == "__main__":
    main()