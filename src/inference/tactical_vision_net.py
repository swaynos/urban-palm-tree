"""
TacticalVisionNet module for EA FC in-match moment tracking.
"""

import torch
from torch import nn
from torchvision import models

class TacticalVisionNet(nn.Module):
    """
    TacticalVisionNet: A dual-branch multi-task neural network for EA FC in-match moment tracking.

    It fuses features from two input images:
    1. Main Pitch View: screenshot resized/cropped to 224x224 (RGB).
    2. Minimap Crop: circular radar crop resized to 224x224 (RGB).

    It predicts three variables:
    1. possession: 3-class classification (0: User, 1: Opponent, 2: Contested/Loose)
    2. zone: 3-class classification (0: Defensive, 1: Middle, 2: Attacking Third)
    3. ball: 2-class continuous regression (pitch_x, pitch_y) in range [0, 1]
    """
    def __init__(self, pretrained=False):
        super().__init__()

        # Determine weights parameter based on pretrained flag and torchvision compatibility
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None

        # Dual-branch feature extractors
        self.main_backbone = models.resnet18(weights=weights)
        self.main_backbone.fc = nn.Identity()

        self.minimap_backbone = models.resnet18(weights=weights)
        self.minimap_backbone.fc = nn.Identity()

        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(512 + 512, 256),
            nn.ReLU(),
            nn.Dropout(0.3)
        )

        # Task Heads
        self.possession_head = nn.Linear(256, 3)
        self.zone_head = nn.Linear(256, 3)
        self.ball_head = nn.Sequential(
            nn.Linear(256, 2),
            nn.Sigmoid()
        )

    def forward(self, main_image, minimap_image):
        """
        Forward pass.

        Args:
            main_image (torch.Tensor): Tensor of shape (Batch, 3, 224, 224)
            minimap_image (torch.Tensor): Tensor of shape (Batch, 3, 224, 224)

        Returns:
            dict: {
                'possession': Tensor of shape (Batch, 3) - possession logits,
                'zone': Tensor of shape (Batch, 3) - zone logits,
                'ball': Tensor of shape (Batch, 2) - normalized ball coordinates [0, 1]
            }
        """
        main_feats = self.main_backbone(main_image)       # (Batch, 512)
        minimap_feats = self.minimap_backbone(minimap_image) # (Batch, 512)

        # Concatenate features along dimension 1
        fused_feats = torch.cat([main_feats, minimap_feats], dim=1) # (Batch, 1024)

        fused = self.fusion(fused_feats) # (Batch, 256)

        # Outputs
        possession = self.possession_head(fused)
        zone = self.zone_head(fused)
        ball = self.ball_head(fused)

        return {
            'possession': possession,
            'zone': zone,
            'ball': ball
        }
