import shinio
import argparse

def main():
    parser = argparse.ArgumentParser(description="Build, run, and deploy madsuite.org website")
    parser.add_argument("action", choices=["build", "cv", "serve", "deploy"], help="Action to perform: build, serve, or deploy")
    args = parser.parse_args()

    if args.action == "build":
        shinio.build()
    if args.action == "cv":
        shinio.cv()
    elif args.action == "serve":
        shinio.serve()
    elif args.action == "deploy":
        shinio.deploy()
        
if __name__ == "__main__":
    main()
