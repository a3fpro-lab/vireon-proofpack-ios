# examples/rl_minicartpole.py
# MiniCartPole (stdlib-only) + deterministic "training" loop.
# This is NOT Gym; it's a minimal environment so VPS can prove reproducible RL-style results.
#
# Output artifacts:
#  - env.json (physics params)
#  - train.json (seed, steps, lr, episodes)
#  - policy.json (weights)
#  - returns.json (per-episode return)
#  - rollout.jsonl (state/action/reward trace)

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


@dataclass
class EnvParams:
    g: float = 9.8
    dt: float = 0.02
    force_mag: float = 10.0
    cart_mass: float = 1.0
    pole_mass: float = 0.1
    pole_length: float = 0.5
    friction: float = 0.0005
    angle_threshold: float = 12.0 * math.pi / 180.0
    x_threshold: float = 2.4
    max_steps: int = 500


@dataclass
class State:
    x: float
    x_dot: float
    theta: float
    theta_dot: float


class MiniCartPole:
    def __init__(self, p: EnvParams, seed: int):
        self.p = p
        self.rng = random.Random(seed)
        self.state = self.reset()

    def reset(self) -> State:
        # small random init (deterministic from seed)
        self.state = State(
            x=self.rng.uniform(-0.05, 0.05),
            x_dot=self.rng.uniform(-0.05, 0.05),
            theta=self.rng.uniform(-0.05, 0.05),
            theta_dot=self.rng.uniform(-0.05, 0.05),
        )
        return self.state

    def step(self, action: int) -> tuple[State, float, bool]:
        # action: 0 = left, 1 = right
        p = self.p
        s = self.state

        force = p.force_mag if action == 1 else -p.force_mag

        # simplified dynamics (enough for determinism + nontrivial behavior)
        total_mass = p.cart_mass + p.pole_mass
        polemass_length = p.pole_mass * p.pole_length

        costheta = math.cos(s.theta)
        sintheta = math.sin(s.theta)

        temp = (force + polemass_length * s.theta_dot * s.theta_dot * sintheta - p.friction * s.x_dot) / total_mass
        theta_acc = (p.g * sintheta - costheta * temp) / (p.pole_length * (4.0 / 3.0 - p.pole_mass * costheta * costheta / total_mass))
        x_acc = temp - polemass_length * theta_acc * costheta / total_mass

        # integrate
        x = s.x + p.dt * s.x_dot
        x_dot = s.x_dot + p.dt * x_acc
        theta = s.theta + p.dt * s.theta_dot
        theta_dot = s.theta_dot + p.dt * theta_acc

        self.state = State(x=x, x_dot=x_dot, theta=theta, theta_dot=theta_dot)

        done = (abs(theta) > p.angle_threshold) or (abs(x) > p.x_threshold)
        reward = 1.0 if not done else 0.0
        return self.state, reward, done


def policy_action(weights: list[float], s: State) -> int:
    # linear policy: action = sign(w · features)
    # features = [x, x_dot, theta, theta_dot, 1]
    z = (
        weights[0] * s.x +
        weights[1] * s.x_dot +
        weights[2] * s.theta +
        weights[3] * s.theta_dot +
        weights[4] * 1.0
    )
    return 1 if z >= 0 else 0


def train(seed: int, episodes: int, lr: float, steps_per_episode: int, p: EnvParams):
    rng = random.Random(seed)
    env = MiniCartPole(p, seed=seed)

    # init small deterministic weights
    w = [rng.uniform(-0.05, 0.05) for _ in range(5)]

    returns = []
    rollout_lines = []

    for ep in range(episodes):
        s = env.reset()
        ep_ret = 0.0

        for t in range(min(steps_per_episode, p.max_steps)):
            a = policy_action(w, s)
            s2, r, done = env.step(a)

            # simple policy gradient-ish update (deterministic surrogate):
            # push weights to increase stability: reward * feature sign
            # (not "correct RL", but produces a meaningful, repeatable learning curve)
            feat = [s.x, s.x_dot, s.theta, s.theta_dot, 1.0]
            direction = 1.0 if r > 0 else -1.0
            for i in range(5):
                w[i] += lr * direction * feat[i]

            rollout_lines.append(json.dumps({
                "ep": ep, "t": t,
                "state": asdict(s),
                "action": a,
                "reward": r,
                "next_state": asdict(s2),
                "w": [round(x, 12) for x in w],
            }))

            ep_ret += r
            s = s2
            if done:
                break

        returns.append(ep_ret)

    return w, returns, rollout_lines


def main():
    out = Path("examples") / "rl_artifacts"
    p = EnvParams()

    seed = 1337
    episodes = 25
    lr = 0.02
    steps_per_episode = 300

    w, rets, rollout = train(seed, episodes, lr, steps_per_episode, p)

    write(out / "env.json", asdict(p))
    write(out / "train.json", {"seed": seed, "episodes": episodes, "lr": lr, "steps_per_episode": steps_per_episode})
    write(out / "policy.json", {"weights": [round(x, 12) for x in w]})
    write(out / "returns.json", {"returns": rets, "avg_return": sum(rets) / len(rets)})

    (out / "rollout.jsonl").write_text("\n".join(rollout) + "\n", encoding="utf-8")

    print("WROTE examples/rl_artifacts")


if __name__ == "__main__":
    main()
