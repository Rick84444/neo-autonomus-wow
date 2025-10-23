import os
from skills.loader import get as get_skill


def test_code_evolve_propose_apply_rollback(tmp_path):
    ce = get_skill("code_evolve")
    # Create a temp file under skills/ to satisfy _safe_path
    skills_dir = os.path.join(os.path.dirname(__file__), "..", "skills")
    os.makedirs(skills_dir, exist_ok=True)
    target_rel = "skills/tmp_test_skill.py"
    target = os.path.join(skills_dir, "tmp_test_skill.py")
    # Use relative path when calling code_evolve (it expects paths rooted in skills/ or ewa/)
    # ensure initial content
    with open(target, "w", encoding="utf-8") as f:
        f.write("# original\nVAR=1\n")

    new_content = "# updated\nVAR=2\n"

    # propose
    res_prop = ce.run("propose", {"path": target_rel, "new_content": new_content}, ctx={})
    assert res_prop.get("ok")
    assert "diff" in res_prop

    # apply (bypass policy by providing confirms)
    res_apply = ce.run("apply", {"path": target_rel, "new_content": new_content, "user_confirm": True, "second_confirm": True}, ctx={})
    assert res_apply.get("ok") and res_apply.get("applied")
    # file content should now be new_content
    with open(target, "r", encoding="utf-8") as f:
        assert f.read() == new_content

    # rollback using backup path from apply response
    backup = res_apply.get("backup")
    res_rb = ce.run("rollback", {"path": target_rel, "backup_path": backup}, ctx={})
    assert res_rb.get("ok") and res_rb.get("rolled_back")
    with open(target, "r", encoding="utf-8") as f:
        assert "original" in f.read()
