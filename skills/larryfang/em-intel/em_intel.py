#!/usr/bin/env python3
"""em-intel: Engineering Manager Intelligence CLI.

Track team performance, engineer contributions, and project health
across GitLab/GitHub + Jira/GitHub Issues.
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("em-intel")


def _get_code_adapter():
    """Create the code platform adapter based on EM_CODE_PROVIDER."""
    provider = os.getenv("EM_CODE_PROVIDER", "gitlab").lower()
    if provider == "github":
        from adapters.github_adapter import GitHubAdapter

        return GitHubAdapter()
    else:
        from adapters.gitlab_adapter import GitLabAdapter

        return GitLabAdapter()


def _get_ticket_adapter():
    """Create the ticket system adapter based on EM_TICKET_PROVIDER."""
    provider = os.getenv("EM_TICKET_PROVIDER", "jira").lower()
    if provider == "github_issues":
        from adapters.github_issues_adapter import GitHubIssuesAdapter

        return GitHubIssuesAdapter()
    else:
        from adapters.jira_adapter import JiraAdapter

        return JiraAdapter()


def _get_project_keys() -> list[str]:
    """Get project keys from env."""
    keys = os.getenv("JIRA_PROJECTS", "")
    return [k.strip() for k in keys.split(",") if k.strip()]


def cmd_morning_brief(args: argparse.Namespace) -> None:
    """Run the morning briefing."""
    from commands.morning_brief import run

    code = _get_code_adapter()
    tickets = _get_ticket_adapter()
    text = run(code, tickets, _get_project_keys())

    if args.send:
        from core.delivery import send

        send(text, title="Morning Brief")


def cmd_eod_review(args: argparse.Namespace) -> None:
    """Run the end-of-day review."""
    from commands.eod_review import run

    code = _get_code_adapter()
    tickets = _get_ticket_adapter()
    text = run(code, tickets, _get_project_keys())

    if args.send:
        from core.delivery import send

        send(text, title="EOD Review")


def cmd_team_report(args: argparse.Namespace) -> None:
    """Run the full team report."""
    from commands.team_report import run

    code = _get_code_adapter()
    tickets = _get_ticket_adapter()
    text = run(code, tickets, _get_project_keys(), days=args.days)

    if args.send:
        from core.delivery import send

        send(text, title="Team Report")


def cmd_contributions(args: argparse.Namespace) -> None:
    """Show branch → ticket contribution map."""
    from rich.console import Console
    from rich.table import Table

    from core.branch_mapper import get_contributions

    console = Console()
    code = _get_code_adapter()
    tickets = _get_ticket_adapter()
    contribs = get_contributions(
        code, tickets, _get_project_keys(), days=args.days, engineer=args.engineer
    )

    if not contribs:
        console.print("[yellow]No branch → ticket mappings found.[/yellow]")
        return

    for engineer, items in sorted(contribs.items()):
        table = Table(title=f"Contributions: {engineer}")
        table.add_column("Ticket", style="cyan")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("Branch", style="dim")
        table.add_column("Days Active", justify="right")
        for c in items:
            table.add_row(c.ticket_id, c.ticket_title, c.ticket_status, c.branch_name, str(c.days_active))
        console.print(table)


def cmd_quiet_engineers(args: argparse.Namespace) -> None:
    """List quiet engineers."""
    from rich.console import Console

    from core.team_pulse import get_quiet_engineers

    console = Console()
    code = _get_code_adapter()
    days = int(os.getenv("EM_QUIET_ENGINEER_DAYS", "10"))
    mrs = code.get_merge_requests(days=30)
    members = list(set(m.author for m in mrs))
    quiet = get_quiet_engineers(mrs, members, days=days)

    if quiet:
        console.print(f"\n[yellow]Quiet engineers (no MR in {days}d):[/yellow]")
        for name in quiet:
            console.print(f"  - {name}")
    else:
        console.print("[green]All engineers are active.[/green]")


def cmd_epic_health(args: argparse.Namespace) -> None:
    """List stale and unassigned epics."""
    from rich.console import Console
    from rich.table import Table

    from core.jira_health import get_stale_epics, get_unassigned_tickets

    console = Console()
    tickets_adapter = _get_ticket_adapter()
    keys = _get_project_keys()
    epics = tickets_adapter.get_epics(keys)
    tickets = tickets_adapter.get_tickets(keys)

    stale_days = int(os.getenv("EM_STALE_EPIC_DAYS", "14"))
    stale = get_stale_epics(epics, days=stale_days)
    unassigned = get_unassigned_tickets(tickets)

    if stale:
        table = Table(title=f"Stale Epics (>{stale_days}d)")
        table.add_column("Key", style="red")
        table.add_column("Title")
        table.add_column("Days Stale", justify="right")
        table.add_column("Assignee")
        for epic in stale:
            table.add_row(epic.key, epic.title, str(epic.days_since_update), epic.assignee or "-")
        console.print(table)
    else:
        console.print("[green]No stale epics.[/green]")

    if unassigned:
        table = Table(title="Unassigned Open Tickets")
        table.add_column("Key", style="yellow")
        table.add_column("Title")
        table.add_column("Priority")
        for t in unassigned[:20]:
            table.add_row(t.key, t.title, t.priority)
        if len(unassigned) > 20:
            console.print(f"  ... and {len(unassigned) - 20} more")
        console.print(table)
    else:
        console.print("[green]No unassigned tickets.[/green]")


def cmd_newsletter(args: argparse.Namespace) -> None:
    """Generate and send the weekly newsletter."""
    from commands.newsletter import run

    code = _get_code_adapter()
    tickets = _get_ticket_adapter()
    run(code, tickets, _get_project_keys(), days=args.week * 7 if args.week else 7)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="em-intel",
        description="Engineering Manager Intelligence — team performance & project health",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # morning-brief
    p_morning = subparsers.add_parser("morning-brief", help="Morning briefing")
    p_morning.add_argument("--send", action="store_true", help="Send via delivery channel")
    p_morning.set_defaults(func=cmd_morning_brief)

    # eod-review
    p_eod = subparsers.add_parser("eod-review", help="End-of-day review")
    p_eod.add_argument("--send", action="store_true", help="Send via delivery channel")
    p_eod.set_defaults(func=cmd_eod_review)

    # team-report
    p_team = subparsers.add_parser("team-report", help="Full team performance report")
    p_team.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    p_team.add_argument("--send", action="store_true", help="Send via delivery channel")
    p_team.set_defaults(func=cmd_team_report)

    # contributions
    p_contrib = subparsers.add_parser("contributions", help="Branch → ticket contribution map")
    p_contrib.add_argument("--engineer", type=str, help="Filter by engineer name")
    p_contrib.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    p_contrib.set_defaults(func=cmd_contributions)

    # quiet-engineers
    p_quiet = subparsers.add_parser("quiet-engineers", help="List quiet engineers")
    p_quiet.set_defaults(func=cmd_quiet_engineers)

    # epic-health
    p_epic = subparsers.add_parser("epic-health", help="Stale epics and unassigned tickets")
    p_epic.set_defaults(func=cmd_epic_health)

    # newsletter
    p_news = subparsers.add_parser("newsletter", help="Generate and send weekly newsletter")
    p_news.add_argument("--week", type=int, default=1, help="Number of weeks to cover (default: 1)")
    p_news.set_defaults(func=cmd_newsletter)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as exc:
        logger.error("Command failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
