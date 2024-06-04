---
title: Agent
emoji: 🌖
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

SOTA open VLM is [InternVL-1.5](https://huggingface.co/spaces/opencompass/open_vlm_leaderboard), which is *22B*, for practical deployment and being GPU poor, I choose moondream which is a model can answer real-world questions about images (378x378). It's tiny by today's models, with only *1.6B* parameters. That enables it to run on a variety of devices, including mobile phones and edge devices.

Other viable altertives under 4B params would be MiniCPM-V-2, PaliGemma-3B-mix-448, and DeepSeek-VL-1.3B.

ToDo:
- [ ] Add a demo video
- [ ] Add retry mechanisms