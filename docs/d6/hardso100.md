# SO-100 Hardware Information

## Hardware overview

- **Robot type:** open-hardware, 6-axis arm consisting of five joints and one gripper.
- **Actuators:** six Feetech STS3215 bus servos connected in a daisy-chain.
- **Communication:** bidirectional TTL serial bus through a USB-to-servo adapter.
- **Power:** use the servo controller's specified supply and wiring; do not power the arm directly from a computer USB port unless the controller is designed for it.
- **Structure:** 3D-printed links and covers with metal servo gearboxes.

## Camera mounting

The camera mount uses **Phillips M3 x 10 mm screws**. Check the screw length against the printed mount and camera bracket before tightening so that the screw does not bottom out or damage the camera housing.

## Bring-up checklist

1. Secure the arm to a stable work surface.
2. Inspect the servo-chain connectors and confirm the motor order before powering on.
3. Connect the USB-to-serial adapter and identify the serial device.
4. Calibrate the arm before teleoperation or data collection.
5. Test each joint at low speed with the emergency stop accessible.
6. Mount and identify the camera only after the arm moves safely without collisions.

## Software references

- [LeRobot SO-100 documentation](https://huggingface.co/docs/lerobot/en/so100)
- [Phosphobot SO-100 quickstart](https://docs.phospho.ai/so-100/quickstart)
- [SO-100 hardware overview](https://www.ay-robots.com/robots/so-100)

