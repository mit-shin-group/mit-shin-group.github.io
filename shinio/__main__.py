import shinio
import argparse

def main():
    parser = argparse.ArgumentParser(description="Build, run, and deploy madsuite.org website")
    parser.add_argument("action", choices=["build", "serve", "deploy"], help="Action to perform: build, serve, or deploy")
    args = parser.parse_args()

    if args.action == "build":
        shinmitedu.build()
    elif args.action == "serve":
        shinmitedu.serve()
    elif args.action == "deploy":
        shinmitedu.deploy()
        
if __name__ == "__main__":
    main()
