"""Incremental mask-aware PPO training and compatible checkpoint resume."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .contract import verify_engine
from .env import TavernEnv

def run(steps:int,seed:int,model_out:Path,resume:Path|None=None):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor
    if steps<128:raise ValueError("steps must be >=128")
    engine=verify_engine()
    env=TavernEnv(seed=seed)
    if resume is not None:
        if not resume.is_file():raise FileNotFoundError(resume)
        meta_path=resume.with_suffix(".metadata.json")
        if not meta_path.is_file():raise ValueError("Missing checkpoint compatibility metadata")
        prev=json.loads(meta_path.read_text(encoding="utf-8"))
        if prev["engine"]!=engine:raise ValueError("Checkpoint engine or card vocabulary mismatch")
        model=MaskablePPO.load(str(resume),env=env,device="cpu")
    else:
        model=MaskablePPO("MultiInputPolicy",env,device="cpu",verbose=1,seed=seed,
            n_steps=128,batch_size=64,n_epochs=4,gamma=0.99,gae_lambda=0.95,
            learning_rate=3e-4,ent_coef=0.01,
            policy_kwargs={"features_extractor_class":TavernExtractor,
              "features_extractor_kwargs":{"features_dim":256},
              "net_arch":{"pi":[128],"vf":[128]}})
    try:
        model.learn(total_timesteps=steps,reset_num_timesteps=False)
        model_out.parent.mkdir(parents=True,exist_ok=True)
        model.save(str(model_out))
        meta={"schema":1,"engine":engine,"total_timesteps":int(model.num_timesteps),
              "training_seed":seed,"algorithm":"MaskablePPO",
              "notes":"V1 CPU single-seat vs seven scripted bots"}
        model_out.with_suffix(".metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
        return meta
    finally:env.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--steps",type=int,default=2048)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--out",type=Path,default=Path("checkpoints/model.zip"))
    p.add_argument("--resume",type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.steps,a.seed,a.out,a.resume),ensure_ascii=False))
if __name__=="__main__":main()
