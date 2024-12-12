import argparse
import sys
from core.repository import Repository
from core.staging import Staging
from core.commit import Commit
from core.history import History
from core.branch import Branch
from core.merge import Merge
from core.diff import Diff
from core.ignore import IgnoreManager

def main():
    parser = argparse.ArgumentParser(description="Distributed Source Control System (DSCS)")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new repository')
    init_parser.add_argument('path', nargs='?', default='.', help='Path to initialize repository (default: current directory)')

    # Add command
    add_parser = subparsers.add_parser('add', help='Stage files for commit')
    add_parser.add_argument('files', nargs='+', help='Files to stage')

    # Commit command
    commit_parser = subparsers.add_parser('commit', help='Commit staged changes')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')

    # Log command
    log_parser = subparsers.add_parser('log', help='View commit history')

    # Branch commands
    branch_parser = subparsers.add_parser('branch', help='Manage branches')
    branch_parser.add_argument('name', nargs='?', help='Branch name to create')
    branch_parser.add_argument('-l', '--list', action='store_true', help='List all branches')

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge branches')
    merge_parser.add_argument('branch', help='Branch to merge into current branch')

    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show differences between branches')
    diff_parser.add_argument('branch1', nargs='?', help='First branch for comparison')
    diff_parser.add_argument('branch2', nargs='?', help='Second branch for comparison')

    # Clone command
    clone_parser = subparsers.add_parser('clone', help='Clone a repository')
    clone_parser.add_argument('source', help='Source repository path')
    clone_parser.add_argument('destination', nargs='?', help='Destination path (optional)')

    # Ignore command
    ignore_parser = subparsers.add_parser('ignore', help='Manage ignored files')
    ignore_parser.add_argument('files', nargs='+', help='Files or patterns to ignore')

    # Parse arguments
    args = parser.parse_args()

    try:
        # Command handling
        if args.command == 'init':
            repo = Repository(args.path)
            repo.initialize()
            print(f"Initialized empty DSCS repository in {args.path}")

        elif args.command == 'add':
            staging = Staging(Repository.find_repo_root())
            for file in args.files:
                staging.add(file)
            print(f"Added {len(args.files)} file(s) to staging")

        elif args.command == 'commit':
            repo = Repository.find_repo_root()
            commit = Commit(repo)
            commit_hash = commit.create(args.message)
            print(f"Created commit {commit_hash}")

        elif args.command == 'log':
            repo = Repository.find_repo_root()
            history = History(repo)
            for commit in history.list_commits():
                print(f"Commit: {commit['hash']}")
                print(f"Message: {commit['message']}")
                print(f"Timestamp: {commit['timestamp']}\n")

        elif args.command == 'branch':
            repo = Repository.find_repo_root()
            branch = Branch(repo)
            if args.list:
                for b in branch.list():
                    print(b)
            elif args.name:
                branch.create(args.name)
                print(f"Created branch {args.name}")

        elif args.command == 'merge':
            repo = Repository.find_repo_root()
            merge = Merge(repo)
            try:
                merge.merge(args.branch)
                print(f"Merged {args.branch} successfully")
            except Exception as e:
                print(f"Merge failed: {e}")

        elif args.command == 'diff':
            repo = Repository.find_repo_root()
            diff = Diff(repo)
            differences = diff.compare_branches(args.branch1, args.branch2)
            for change in differences:
                print(change)

        elif args.command == 'clone':
            repo = Repository(args.source)
            destination = args.destination or repo.name
            repo.clone(destination)
            print(f"Cloned repository to {destination}")

        elif args.command == 'ignore':
            repo = Repository.find_repo_root()
            ignore_manager = IgnoreManager(repo)
            for pattern in args.files:
                ignore_manager.add(pattern)
            print(f"Added {len(args.files)} pattern(s) to .dscsignore")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()