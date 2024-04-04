# urban-palm-tree

## Project Goals
1. While in game, perform user input to keep the user from being kicked out as inactive
2. While out of game, navigate the menu's to place the user back into a game
3. End to end testing. Automation will navigate the menus's and place the user into a game, automating some input to prevent from being kicked out
4. Consider this use case: https://www.youtube.com/watch?v=DcYLT37ImBY
    ### Summary (mistral:7b-instruct-v0.2-q4_K_M)
    In this project, we explore creating an autonomous Pokemon master using 
    deep reinforcement learning. We'll discuss the project's goals, 
    techniques, metrics & visualization, and future improvements.

    Goals:
    1. Develop an AI that can play and learn from the Pokemon Red game.
    2. Optimize for long-term strategy while performing fine-grained 
    movements.
    3. Create a scalable framework to accommodate various games and
    environments.

    Techniques:
    1. Extract features using convolutional neural networks (CNNs).
    2. Apply Q-learning algorithm with deep neural networks as function 
    approximators.
    3. Use monte carlo tree search for policy evaluation.
    4. Implement exploration strategies like epsilon-greedy and UCB1.
    5. Train the model in parallel on multiple CPUs/GPUs.

    Metrics & Visualization:
    1. Player coordinates and Pokemon stats are recorded at every step.
    2. Thousands of videos are rendered and combined to create a giant game 
    grid.
    3. Flow visualization is made using the same player data.
    4. Rewards are calculated based on Pokemon levels, health, and trainer's 
    progress.

    Future Improvements:
    1. Transfer learning with pre-trained models for new tasks.
    2. Use deep Q-networks (DQN) or proximal policy optimization (PPO) 
    algorithms for better performance and convergence.
    3. Implement memory replay techniques to improve exploration.
    4. Implement more complex reward functions, such as taking into account 
    the strengths and weaknesses of both the player's team and the opponent's 
    team.
    5. Explore using other machine learning techniques, like genetic 
    algorithms or reinforcement learning with deep belief networks (DBNs), for
    training the AI.
    6. Investigate multi-agent reinforcement learning to train multiple 
    Pokemon at once and optimize their abilities and moves collaboratively.
    7. Create a web interface that allows users to interact with the game and 
    monitor the AI's progress in real-time.
    8. Expand this project to other Pokemon games, such as Gold/Silver or 
    Crystal.
    9. Integrate the trained model into real-life game platforms like 
    emulators or console modding.

    Conclusion:
    By creating an autonomous Pokemon master using deep reinforcement 
    learning, we can gain valuable insights into both machine learning and 
    psychology. This project showcases the power of deep learning algorithms 
    to learn complex strategies in video games and offers a unique opportunity
    to study human behavior by observing an AI that mimics our actions while 
    outperforming us in various scenarios.