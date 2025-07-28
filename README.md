# AI Hacking Challenges

This repository contains a collection of dockerized AI/LLM hacking challenges in various difficulties. The goal of each challenge is to leak a flag in the format FLG{flag_is_in_here}.

The repository allows you to spawn fully functional, local LLM instances and experiment with their behavior and various security mechanisms. Feel free to explore the code and further your LLM security knowledge.

## Overview of Challenges

![chatLOL preview](chatlol-demo.png)

**[chatLOL](/chatlol/)**
This LLM challenge uses the llama3.2:1b model to implement basic chatbot functionality. The LLM was instructed not to disclose the flag via a custom system prompt.

**[chatLOL2](/chatlol2/)** This LLM challenge uses the llama3.2:1b model to implement basic chatbot functionality. In addition to a custom system prompt the challenge employs the protectai/deberta-v3-base-prompt-injection-v2 model to filter malicious messages.

## Build

The build and run instructions for each challenge can be found in the subsequent challenge folders.