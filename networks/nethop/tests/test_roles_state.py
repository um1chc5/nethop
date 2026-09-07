"""Lightweight checks for roles / export / state (no nmap required)."""

from __future__ import annotations

from nethop.export import host_card
from nethop.models import Host, Port
from nethop.roles import guess_role
from nethop.state import AppState


def test_k8s_role_from_port() -> None:
    h = Host(ip="10.0.0.5", ports=[Port(6443)])
    assert guess_role(h) == "k8s"


def test_bastion_from_hostname() -> None:
    h = Host(ip="10.0.0.6", hostname="jump-bastion-01")
    assert guess_role(h) == "bastion"


def test_ssh_only() -> None:
    h = Host(ip="10.0.0.7", ports=[Port(22)])
    assert guess_role(h) == "ssh"


def test_nickname_state() -> None:
    s = AppState()
    s.set_nickname("10.0.0.1", " api ")
    assert s.nickname_for("10.0.0.1") == "api"
    s.set_nickname("10.0.0.1", "")
    assert s.nickname_for("10.0.0.1") == ""


def test_host_card_contains_role() -> None:
    h = Host(ip="10.0.0.8", role="postgres", ports=[Port(5432, service="postgresql")])
    text = host_card(h)
    assert "postgres" in text
    assert "5432" in text


if __name__ == "__main__":
    test_k8s_role_from_port()
    test_bastion_from_hostname()
    test_ssh_only()
    test_nickname_state()
    test_host_card_contains_role()
    print("ok")
