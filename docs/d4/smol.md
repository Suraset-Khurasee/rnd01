---
layout: default
title: SmolVLA
---

# SmolVLA (Small Vision-Language-Action Model)

## 1. Introduction

SmolVLA is an open-source Vision-Language-Action model developed by Hugging Face in 2025. It contains approximately **450 million parameters** and is designed to make robotic foundation models more accessible by reducing computational requirements while maintaining competitive performance [1].

## 2. Basic Properties

- **Model Size:** Approximately 450 million parameters.
- **Developer:** Hugging Face.
- **Architecture:** Uses SmolVLM2 as its vision-language backbone, alongside a separate action expert.
- **Action Generation:** Uses Flow Matching to generate continuous action chunks.
- **Training:** Uses diverse robotic demonstration datasets, followed by task-specific fine-tuning.
- **Deployment:** Designed to operate on consumer-grade hardware, making it more accessible for research and experimentation [1][2].

## 3. Similarities and Differences Between SmolVLA and π₀.₅

### 3.1 Similarities

1. Both are open-source Vision-Language-Action models designed for robotic manipulation.
2. Both use a vision-language backbone to process visual observations and natural-language instructions.
3. Both employ Flow Matching to generate continuous robotic actions.
4. Both can be fine-tuned using robot-specific demonstrations to adapt to different robotic tasks.

### 3.2 Differences

| Feature | SmolVLA | π₀.₅ |
|---|---|---|
| **Developer** | Hugging Face | Physical Intelligence |
| **Model Size** | Approximately 450M parameters | Approximately 3B parameters |
| **Main Objective** | Improve accessibility and computational efficiency. | Improve generalisation to unfamiliar environments and tasks. |
| **Architecture** | SmolVLM2 backbone with a separate action expert. | Vision-language architecture with high-level and low-level inference components. |
| **Training Approach** | Pretraining on curated community-contributed robotic datasets, followed by fine-tuning. | Heterogeneous co-training using robotic demonstrations, web data and semantic task information. |


## 4. Relevance to This Project

SmolVLA is a potential candidate for the AgileX NERO teleoperation project because of its relatively small model size and lower computational requirements. Its asynchronous inference mechanism may also help improve responsiveness during robotic operation.

In comparison, π₀.₅ places greater emphasis on generalisation to unfamiliar environments through its high-level and low-level inference architecture.

Therefore, the choice between these models should depend on the project's priorities: computational efficiency and accessibility versus more advanced generalisation capabilities.

## 5. References

[1] [Hugging Face. *SmolVLA: Efficient Vision-Language-Action Model.*](https://huggingface.co/blog/smolvla)

[2] [SmolVLA Research Paper. *SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics.*](https://smolvla.net/paper_en)

[3] [Physical Intelligence. *π₀.₅: A Vision-Language-Action Model with Open-World Generalization.*](https://www.pi.website/download/pi05.pdf)