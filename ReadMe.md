# Project Statement

We aim to build a tool that turns natural language descriptions of multi-agent systems into executable code. By leveraging large language models to convert language into precise LTL specifications and employing reactive synthesis techniques, we bridge the gap between conceptual design and system realization. This tool empowers users to observe, interact with, and control the dynamic behaviors of interconnected agents.

# Tool Structure

We take in a natural language prompt describing a task we want our system of agents to perform, a set of constraints for the game (such as players cannot collide), and a specified number of agents to occupy the system. Through prompt engineering and seeding, we rely on the LLM to output an LTL formulation, a system player, and an environment player in the form of a JSON. We then play a parity game and determine whether this LTL sequence is realizable. If it is realizable, we pass the LTL along with the initial prompt back into the LLM to generate code for the agents that will populate the scene. While it is possible for this process to produce a realizable scene, it is more difficult for us to determine—without checking—whether the scene produced accurately depicts our intended design.

# What Are Multi Agent Systems

In our experiment, multi-agent systems are systems in which many distinct agents navigate the scene independently. These agents are bounded by the constraints of the LTL formulation. Although the specific constraints vary from game to game, at a high level, all agents must satisfy the safety and liveness requirements of the system. In every system, collisions between agents or with the environment are not allowed.

# Project Setup

We are testing how well a multi-agent planning tool works on a series of games and scenes. A scene is a 10x10 grid with black and white squares. The black squares represent obstacles and walls, while the white squares represent open spaces. Each game features _N_ specified agents, each depicted in a distinct color (excluding black and white). For team games, such as Cops and Robbers, agents from the same team share the same color. The goal is to understand how well LLMs can faithfully implement complex multi-agent problems by transforming them into reactive synthesis problems.
