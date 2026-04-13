from __future__ import annotations

import torch
import torch.nn as nn

from gomoku.config import BOARD_SIZE, ACTION_SIZE


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(channels)

        self.conv2 = nn.Conv2d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(channels)

        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out = out + identity
        out = self.relu(out)

        return out


class PolicyValueNet(nn.Module):
    def __init__(self, in_channels: int = 4, channels: int = 64, num_blocks: int = 4):
        super().__init__()

        self.relu = nn.ReLU(inplace=True)

        # stem
        self.stem_conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=channels,
            kernel_size=3,
            padding=1,
            bias=False,
        )
        self.stem_bn = nn.BatchNorm2d(channels)

        # backbone
        blocks = []
        for _ in range(num_blocks):
            blocks.append(ResidualBlock(channels))
        self.backbone = nn.Sequential(*blocks)

        # policy head
        self.policy_conv = nn.Conv2d(
            in_channels=channels,
            out_channels=2,
            kernel_size=1,
            bias=False,
        )
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_fc = nn.Linear(2 * BOARD_SIZE * BOARD_SIZE, ACTION_SIZE)

        # value head
        self.value_conv = nn.Conv2d(
            in_channels=channels,
            out_channels=1,
            kernel_size=1,
            bias=False,
        )
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(BOARD_SIZE * BOARD_SIZE, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # stem
        x = self.stem_conv(x)
        x = self.stem_bn(x)
        x = self.relu(x)

        # backbone
        x = self.backbone(x)

        # policy head
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = self.relu(p)
        p = torch.flatten(p, start_dim=1)
        policy_logits = self.policy_fc(p)

        # value head
        v = self.value_conv(x)
        v = self.value_bn(v)
        v = self.relu(v)
        v = torch.flatten(v, start_dim=1)
        v = self.value_fc1(v)
        v = self.relu(v)
        v = self.value_fc2(v)
        value = torch.tanh(v)

        return policy_logits, value


def load_model(checkpoint_path: str, device: str = "cpu") -> PolicyValueNet:
    model = PolicyValueNet()
    model.to(device)

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()
    return model