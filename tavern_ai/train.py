"""Incremental mask-aware PPO training and compatible checkpoint resume."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from .contract import verify_engine
from .checkpoint_preflight import audit_archive
from .env import TavernEnv

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_resume(resume: Path, engine: dict, expected_sha256: str | None = None) -> dict:
    """Validate ZIP/optimizer and exact metadata BEFORE SB3 loads a checkpoint.

    For trusted external Releases, pass an independently recorded SHA256.
    A digest read from the same checkpoint metadata is only a consistency
    check, not independent provenance; legacy schema-1 files without a digest
    retain a bounded structural/CRC check for backwards compatibility.
    """
    resume = Path(resume)
    if not resume.is_file():
        raise FileNotFoundError(resume)
    meta_path = resume.with_suffix(".metadata.json")
    if not meta_path.is_file():
        raise ValueError("Missing checkpoint compatibility metadata")
    previous = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(previous, dict) or previous.get("engine") != engine:
        raise ValueError("Checkpoint engine or card vocabulary mismatch")
    expected = expected_sha256
    if expected is None:
        expected = previous.get("checkpoint_sha256")
    if expected is None:
        expected = sha256_file(resume)
    audit_archive(resume, meta_path, expected)
    return previous


def run(steps:int,seed:int,model_out:Path,resume:Path|None=None,
        resume_sha256:str|None=None):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor
    if steps<128:raise ValueError("steps must be >=128")
    engine=verify_engine()
    env=TavernEnv(seed=seed)
    if resume is not None:
        prev = inspect_resume(resume, engine, resume_sha256)
        model=MaskablePPO.load(str(resume),env=env,device="cpu")
        if type(model.num_timesteps) is not int or model.num_timesteps != prev["total_timesteps"]:
            raise ValueError("Loaded PPO step count differs from checkpoint metadata")
    else:
        if resume_sha256 is not None:
            raise ValueError("--resume-sha256 requires --resume")
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
              "checkpoint_sha256":sha256_file(model_out),
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
    p.add_argument("--resume-sha256",help="Trusted external SHA256 for resume weights (required to claim independent provenance)")
    a=p.parse_args()
    print(json.dumps(run(a.steps,a.seed,a.out,a.resume,a.resume_sha256),ensure_ascii=False))
if __name__=="__main__":main()
