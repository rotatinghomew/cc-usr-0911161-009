from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from public_service_sla.service_monitor import Application, run, verify


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='public_service_sla', description='国际人工智能公共产品服务水平观测台')
    cli = root.add_subparsers(dest="command", required=True)
    execute = cli.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    check = cli.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    inspect = cli.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "run":
        result = run(args.fixture, args.database, args.output)
    elif args.command == "verify":
        result = verify(args.database, args.output)
    else:
        result = Application(args.database).inspect()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
