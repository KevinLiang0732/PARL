from main import train
from policy_model import CDPModel_DQN_with_pretrain
import os

if __name__=="__main__":
    import ray
    from ray.rllib.algorithms.alpha_zero import AlphaZeroConfig
    from env import ACTION_SPACE, OBSERVATION_SPACE_LITE_DICT
    os.environ['CUDA_VISIBLE_DEVICES']='0'
    ray.init(num_cpus=6)
    # weight_root = "./weights/pretrain/user_repr_pt_new_data_v2_1678128493"
    weight_root = "./weights/pretrain/TDQN_new_datadist_v4"
    restore_root = "./models/experiment_MVR2D2_ptv3_full_LEN100_1680802237"
    # obj = torch.load(os.path.join(weight_root, "state_dict.pt"))
    # print(obj.__class__)
    # torch.save(model.state_dict(), os.path.join(weight_root, "state_dict.pt"))
    # train("MVDQN_ptv2_org_easy", weight_path=os.path.join(weight_root, "state_dict.pt"))
    # pretrain_embeddings()
    ###############################################################################
    # train MVDQN_ptv2 params
    ###############################################################################
    config = {
        # Environment (RLlib understands openAI gym registered strings).
        # Use 2 environment workers (aka "rollout workers") that parallelly
        # collect samples from their own environment clone(s).
        "disable_env_checking": True,
        "env": "OrderEnv-v2",
        "env_config": {
            "num_cars": 3, 
            "num_couriers": 1,
            "max_episode_length": 100,
            # DEPRECATED
            # "robot_reward_scale": 2.5, 
            # "entropy_reward_scale": 2,
            "wrap_obs": False, 
            "use_gymnasium": True,
            "random_episode": True,
            "coeff": {
                "robot_reward_scale": 2,
                "entropy_reward_scale": 2.5,
                "delv_reward_scale": 5,
                "wb_reward_scale": 1,
                "reg_scale": 0.05
            }

        },
        "num_workers": 6,
        "num_gpus": 1,
        # Change this to "framework: torch", if you are using PyTorch.
        # Also, use "framework: tf2" for tf2.x eager execution.
        "framework": "torch",
        # Tweak the default model provided automatically by RLlib,
        # given the environment's observation- and action spaces.
        "model": {
            "custom_model": CDPModel_DQN_with_pretrain,
            # Extra kwargs to be passed to your model's c'tor.
            "custom_model_config": {
            },
        },

        "min_sample_timesteps_per_iteration": 1000,
        "replay_buffer_config":{
          "type": "MultiAgentReplayBuffer",
          "capacity": 200000,
        },

        # "entropy_coeff": 0.05,
        "exploration_config": {
            "type": "EpsilonGreedy",
            "initial_epsilon": 1.0,
            "final_epsilon": 0.01,
            "epsilon_timesteps": 1000 * 1000,
        },
        "train_batch_size": 64,
        "lr": 5e-4,
        "lr_schedule": [
        [
            0,
            0.0005
        ],
        [
            800000,
            0.0005
        ],
        [
            1500000,
            0.00025
        ],
        [
            3000000,
            0.000125
        ]
    ],
    }
    
    #######################
    train(
        "MVDQN_ptv4_full_RAN300_c3_r", 
        weight_path=None, # os.path.join(weight_root, "state_dict.pt"),
        config=config,
        iterations=2000,
        restore_path=None
    )

    #######################
    
    ########################
    # ENT ablation study
    # train(
    #     "MVDQN_ptv2_woent_dm_LEN100_retrain", 
    #     weight_path=os.path.join(weight_root, "state_dict.pt"),
    #     config=config,
    #     iterations=10000,
    #     restore_path=None
    # )
    ########################

    ########################
    # PT ablation study
    # train(
    #     "MVDQN_woptv2_ent_dm_LEN100_retrain", 
    #     weight_path=None,
    #     config=config,
    #     iterations=10000,
    #     restore_path=None
    # )
    ########################
    
    # train("MVTDQN_ptv3_ent_dm_LEN300", weight_path=os.path.join(weight_root, "state_dict.pt"),
    #       config=config,
    #       iterations=10000,
    #       restore_path=None)
    # evaluate(algo_cls=DQN, restore_path="models/experiment_MVDQN_ptv2_org_LEN50_retrain_1678885630/saved_ckpt", config=config)
    ray.shutdown()