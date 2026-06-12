"""
Tests for TacticalVisionNet model shape and gradient propagation.
"""

import torch
from torch import nn
from inference.tactical_vision_net import TacticalVisionNet

def test_model_shape_verification():
    """
    Test 1: Model Shape Verification.
    Verifies that the forward pass succeeds and outputs correct tensor shapes.
    """
    batch_size = 4
    model = TacticalVisionNet(pretrained=False)
    model.eval()  # Put in evaluation mode

    # Create dummy input tensors
    main_image = torch.randn(batch_size, 3, 224, 224)
    minimap_image = torch.randn(batch_size, 3, 224, 224)

    with torch.no_grad():
        outputs = model(main_image, minimap_image)

    assert isinstance(outputs, dict), "Outputs should be a dictionary"
    assert "possession" in outputs, "possession key should be in outputs"
    assert "zone" in outputs, "zone key should be in outputs"
    assert "ball" in outputs, "ball key should be in outputs"

    p_shape = outputs["possession"].shape
    z_shape = outputs["zone"].shape
    b_shape = outputs["ball"].shape

    assert p_shape == (batch_size, 3), f"Expected possession shape {(batch_size, 3)}, got {p_shape}"
    assert z_shape == (batch_size, 3), f"Expected zone shape {(batch_size, 3)}, got {z_shape}"
    assert b_shape == (batch_size, 2), f"Expected ball shape {(batch_size, 2)}, got {b_shape}"


def test_gradient_propagation_verification():
    """
    Test 2: Gradient Propagation Verification.
    Verifies that the backward pass successfully propagates gradients to all parameters.
    """
    # pylint: disable=too-many-locals
    batch_size = 2
    model = TacticalVisionNet(pretrained=False)
    model.train()  # Put in training mode

    # Create dummy input tensors
    main_image = torch.randn(batch_size, 3, 224, 224)
    minimap_image = torch.randn(batch_size, 3, 224, 224)

    # Create dummy target labels
    target_possession = torch.tensor([0, 1], dtype=torch.long)
    target_zone = torch.tensor([1, 2], dtype=torch.long)
    target_ball = torch.tensor([[0.2, 0.3], [0.8, 0.9]], dtype=torch.float)

    # Run forward pass
    outputs = model(main_image, minimap_image)

    # Compute multi-task loss using default weights from SPEC.md
    w_possession = 1.0
    w_zone = 1.0
    w_ball = 10.0

    criterion_classification = nn.CrossEntropyLoss()
    criterion_regression = nn.MSELoss()

    loss_possession = criterion_classification(outputs["possession"], target_possession)
    loss_zone = criterion_classification(outputs["zone"], target_zone)
    loss_ball = criterion_regression(outputs["ball"], target_ball)

    total_loss = w_possession * loss_possession + w_zone * loss_zone + w_ball * loss_ball

    # Backward pass
    total_loss.backward()

    # Check that all trainable parameters have non-null, non-zero gradients
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Parameter {name} grad is None"
            assert torch.sum(torch.abs(param.grad)) > 0, f"Parameter {name} has zero gradient"
