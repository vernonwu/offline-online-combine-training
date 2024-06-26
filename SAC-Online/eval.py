import gym
import numpy as np
import torch
import argparse
from utils import save, collect_random
from agent import SAC


def get_config():
    parser = argparse.ArgumentParser(description='RL')
    parser.add_argument("--run_name", type=str, default="SAC",)
    parser.add_argument("--env", type=str, default="LunarLander-v2")
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--buffer_size", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--log_video", type=int, default=0)
    parser.add_argument("--save_every", type=int, default=100)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--n_episode", type=int, default=1000)
    parser.add_argument("--n_steps_max", type=int, default=1000)
    args = parser.parse_args()
    return args


def eval(config):
    env = gym.make(config.env)
    env.seed(config.seed)
    env.action_space.seed(config.seed)

    env1 = gym.make(config.env)
    env1.seed(config.seed)
    env1.action_space.seed(config.seed)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    agent_online = SAC(state_size=env.observation_space.shape[0],
                         action_size=env.action_space.n,
                         device=device)
    agent_combine = SAC(state_size=env.observation_space.shape[0],
                         action_size=env.action_space.n,
                         device=device)
    online_actor_state_dict = torch.load("trained_models/SACSAC_discrete0.pth", map_location=device)
    combine_actor_state_dict = torch.load(f"trained_models/CQL-SAC-discreteCQL-SAC-discrete{config.episodes}.pth", map_location=device)
    agent_online.actor_local.load_state_dict(online_actor_state_dict)
    agent_combine.actor_local.load_state_dict(combine_actor_state_dict)
    n_episode = config.n_episode

    max_step = config.n_steps_max

    online_return = []

    for i in range(n_episode):
        state = env.reset()
        done = False
        episode_return = 0
        step = 0
        while not done and step < max_step:
            action = agent_online.get_action(state)
            next_state, reward, done, _ = env.step(action)
            episode_return += reward
            state = next_state
            step += 1

        online_return.append(episode_return)
    online_return = np.array(online_return)

        # paths.append([state_list, action_list, reward_list, next_state_list, done_list])

    print(f"Online Return Mean: {online_return.mean()} || Std: {online_return.std()}")


    combine_return = []

    for i in range(n_episode):
        state = env1.reset()
        done = False
        episode_return = 0
        step = 0
        while not done and step < max_step:
            action = agent_combine.get_action(state)
            next_state, reward, done, _ = env1.step(action)
            episode_return += reward
            state = next_state
            step += 1

        combine_return.append(episode_return)
    combine_return = np.array(combine_return)

    print(f"Combine Return Mean: {combine_return.mean()} || Std: {combine_return.std()}")

if __name__ == "__main__":
    config = get_config()
    eval(config)