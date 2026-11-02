"""Incremental mask-aware PPO training and compatible checkpoint resume."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .registry_integrity import verify_checkpoint
from .contract import verify_engine
from .env import TavernEnv


def validate_resume_metadata(resume: Path, engine: dict) -> dict:
    """Check sidecar/weight consistency before loading PPO.

    Schema-1 archives without a digest are historical and remain loadable;
    they are NOT certified as integrity-checked. New saves include SHA-256.
    A self-attested digest detects accidental damage, not malicious tampering;
    trusted Release provenance is a separate gate.
    """
    if not resume.is_file():
        raise FileNotFoundError(resume)
    sidecar = resume.with_suffix(".metadata.json")
    if not sidecar.is_file():
        raise ValueError("Missing checkpoint compatibility metadata")
    prev = json.loads(sidecar.read_text(encoding="utf-8"))
    if not isinstance(prev, dict) or prev.get("schema") not in (1, 2):
        raise ValueError("Invalid checkpoint metadata schema")
    if prev.get("engine") != engine:
        raise ValueError("Checkpoint engine or card vocabulary mismatch")
    steps = prev.get("total_timesteps")
    if type(steps) is not int or steps <= 0:
        raise ValueError("Invalid checkpoint cumulative timesteps")
    digest = prev.get("checkpoint_sha256")
    if digest is None:
        if prev["schema"] == 2:
            raise ValueError("Schema-2 checkpoint requires SHA-256")
    else:
        verify_checkpoint(resume, digest)
    return prev

def run(steps:int,seed:int,model_out:Path,resume:Path|None=None):
    if steps<128:raise ValueError("steps must be >=128")
    engine=verify_engine()
    previous = validate_resume_metadata(resume, engine) if resume is not None else None
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor
    env=TavernEnv(seed=seed)
    if resume is not None:
        model=MaskablePPO.load(str(resume),env=env,device="cpu")
        if type(model.num_timesteps) is not int or model.num_timesteps != previous["total_timesteps"]:
            env.close()
            raise ValueError("Checkpoint model/sidecar cumulative timesteps mismatch")
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
        # Hash completed checkpoint bytes before writing the resumable sidecar.
        from .registry_integrity import verify_checkpoint as _verify
        import hashlib
        digest=hashlib.sha256(model_out.read_bytes()).hexdigest()
        _verify(model_out,digest)
        meta={"schema":1,"engine":engine,"total_timesteps":int(model.num_timesteps),
              "training_seed":seed,"algorithm":"MaskablePPO",
              "checkpoint_sha256":digest,
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
