import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import local_identity_pipeline as pipeline


class LocalIdentityPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.tempdir.name)
        self.run_id = "2099-01-01_test-run"
        self.run_root = self.repo_root / "runs" / self.run_id
        (self.run_root / "references-used").mkdir(parents=True)
        (self.run_root / "evals").mkdir()

        self.files = {
            "references/identity/aachu/face/aachu-face-crop-a.jpg": b"aachu crop a",
            "references/identity/aachu/face/aachu-face-crop-b.jpg": b"aachu crop b",
            "references/identity/aachu/face/aachu-face-crop-c.jpg": b"aachu crop c",
            "references/identity/aachu/face/aachu-face-crop-d.jpg": b"aachu crop d",
            "references/identity/aachu/smiles/aachu-smile-a.jpg": b"aachu smile a",
            "references/identity/zuv/face/zuv-face-crop-a.jpg": b"zuv crop a",
            "references/identity/zuv/face/zuv-face-crop-b.jpg": b"zuv crop b",
            "references/identity/zuv/face/zuv-face-crop-c.jpg": b"zuv crop c",
            "references/identity/zuv/face/zuv-face-crop-d.jpg": b"zuv crop d",
            "references/identity/zuv/smiles/zuv-smile-a.jpg": b"zuv smile a",
            "references/identity/together/face-and-body-language/together-a.jpg": b"together role bytes",
            "references/wardrobe/aachu/aachu-wardrobe-a.jpg": b"aachu wardrobe bytes",
            "references/places/place-a.jpg": b"place bytes",
            "references/identity/_dossier/identity-face-contact-sheet.jpg": b"face sheet bytes",
            "references/identity/_dossier/identity-expressions-contact-sheet.jpg": b"expression sheet bytes",
            "references/style/observational-intimacy-premium/contact-sheet.png": b"style bytes",
        }
        for rel_path, content in self.files.items():
            path = self.repo_root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        selected_references = {
            "run_id": self.run_id,
            "identity_references": {
                "aachu": [
                    "references/identity/aachu/face/aachu-face-crop-a.jpg",
                    "references/identity/aachu/face/aachu-face-crop-b.jpg",
                ],
                "zuv": [
                    "references/identity/zuv/face/zuv-face-crop-a.jpg",
                    "references/identity/zuv/face/zuv-face-crop-b.jpg",
                ],
                "together": [
                    "references/identity/together/face-and-body-language/together-a.jpg"
                ],
            },
            "style_references": [
                "references/style/observational-intimacy-premium/contact-sheet.png"
            ],
        }
        (self.run_root / "references-used" / "selected_references.json").write_text(
            json.dumps(selected_references), encoding="utf-8"
        )
        self.write_identity_dossier()

    def tearDown(self):
        self.tempdir.cleanup()

    def build_proof(self, **kwargs):
        return pipeline.build_local_identity_reference_proof(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_id="option_b_sdxl_instantid_pulid_ipadapter",
            **kwargs,
        )

    def write_identity_proof_runtime_files(self, hardware_status=None, failure_code=None):
        workflow = self.run_root / "local-workflows" / "identity-proof-comfyui.json"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text(
            json.dumps(
                {
                    "4": {
                        "class_type": "CheckpointLoaderSimple",
                        "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
                    },
                    "13": {
                        "class_type": "LoadImage",
                        "inputs": {
                            "image": "astory_identity_proof/aachu_face_anchor.jpg"
                        },
                    },
                    "78": {
                        "class_type": "LoadImage",
                        "inputs": {
                            "image": "astory_identity_proof/zuv_face_anchor.jpg"
                        },
                    },
                    "82": {
                        "class_type": "LoadImage",
                        "inputs": {
                            "image": "astory_identity_proof/together_pose_context.jpg"
                        },
                    },
                    "60": {"class_type": "ApplyInstantID", "inputs": {}},
                    "77": {"class_type": "ApplyInstantID", "inputs": {}},
                }
            ),
            encoding="utf-8",
        )

        input_dir = self.run_root / "local-tools" / "ComfyUI" / "input" / "astory_identity_proof"
        input_dir.mkdir(parents=True, exist_ok=True)
        input_bytes = {
            "aachu_face_anchor.jpg": b"aachu crop a",
            "zuv_face_anchor.jpg": b"zuv crop a",
            "together_pose_context.jpg": b"together role bytes",
        }
        for filename, content in input_bytes.items():
            (input_dir / filename).write_bytes(content)

        model_bytes = {
            "checkpoints/sd_xl_base_1.0.safetensors": b"fake sdxl",
            "instantid/ip-adapter.bin": b"fake instantid adapter",
            "controlnet/instantid-controlnet.safetensors": b"fake instantid controlnet",
        }
        model_root = self.run_root / "local-tools" / "ComfyUI" / "models"
        for rel_path, content in model_bytes.items():
            path = model_root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        def input_record(role, filename):
            rel_path = (
                f"runs/{self.run_id}/local-tools/ComfyUI/input/"
                f"astory_identity_proof/{filename}"
            )
            return {
                "role": role,
                "path": rel_path,
                "sha256": hashlib.sha256(input_bytes[filename]).hexdigest(),
            }

        execution_report = {
            "run_id": self.run_id,
            "status": "blocked" if failure_code else "not_run_after_readiness",
            "failure_code": failure_code,
            "final_artwork_generated": False,
            "identity_proof_generated": False,
            "workflow_inputs": [
                input_record("aachu_face_anchor", "aachu_face_anchor.jpg"),
                input_record("zuv_face_anchor", "zuv_face_anchor.jpg"),
                input_record("together_pose_context", "together_pose_context.jpg"),
            ],
            "model_stack": {
                "base_checkpoint": {
                    "path": (
                        f"runs/{self.run_id}/local-tools/ComfyUI/models/"
                        "checkpoints/sd_xl_base_1.0.safetensors"
                    ),
                    "sha256": hashlib.sha256(
                        model_bytes["checkpoints/sd_xl_base_1.0.safetensors"]
                    ).hexdigest(),
                },
                "identity_adapter": {
                    "path": (
                        f"runs/{self.run_id}/local-tools/ComfyUI/models/"
                        "instantid/ip-adapter.bin"
                    ),
                    "sha256": hashlib.sha256(
                        model_bytes["instantid/ip-adapter.bin"]
                    ).hexdigest(),
                },
                "controlnet": {
                    "path": (
                        f"runs/{self.run_id}/local-tools/ComfyUI/models/"
                        "controlnet/instantid-controlnet.safetensors"
                    ),
                    "sha256": hashlib.sha256(
                        model_bytes["controlnet/instantid-controlnet.safetensors"]
                    ).hexdigest(),
                },
            },
            "attempts": [
                {
                    "prompt_id": "test-prompt",
                    "status": "interrupted_blocked",
                    "observed_progress": "0/4",
                }
            ]
            if failure_code
            else [],
            "hardware_status": hardware_status
            or {
                "mps_available": False,
                "mps_built": True,
                "cuda_available": False,
                "effective_execution_device": "cpu",
            },
        }
        report_path = self.run_root / "evals" / "local_identity_execution_report.json"
        report_path.write_text(json.dumps(execution_report), encoding="utf-8")
        return workflow, execution_report

    def ready_discovery(self):
        return {
            "status": "ready_for_creator_execution_approval",
            "failure_codes": [],
        }

    def write_identity_dossier(self, override_refs=None):
        dossier_path = self.repo_root / "references/identity/_dossier/identity-dossier.json"
        dossier_path.parent.mkdir(parents=True, exist_ok=True)

        def ref(rel_path, subject, role, quality="primary"):
            return {
                "id": f"TEST{len(imported) + 1:03d}",
                "path": rel_path,
                "filename": Path(rel_path).name,
                "subject": subject,
                "role": role,
                "use_for": ["face_identity"] if role == "face_anchor" else [role],
                "do_not_use_for": ["place_reference"]
                if role == "face_anchor"
                else ["face_identity"],
                "quality": quality,
                "source_path": f"/test-source/{Path(rel_path).name}",
                "source_filename": Path(rel_path).name,
                "width": 100,
                "height": 100,
                "sha256": hashlib.sha256((self.repo_root / rel_path).read_bytes()).hexdigest(),
            }

        imported = []
        for rel_path in [
            "references/identity/aachu/face/aachu-face-crop-a.jpg",
            "references/identity/aachu/face/aachu-face-crop-b.jpg",
            "references/identity/aachu/face/aachu-face-crop-c.jpg",
            "references/identity/aachu/face/aachu-face-crop-d.jpg",
        ]:
            imported.append(ref(rel_path, "aachu", "face_anchor"))
        for rel_path in [
            "references/identity/zuv/face/zuv-face-crop-a.jpg",
            "references/identity/zuv/face/zuv-face-crop-b.jpg",
            "references/identity/zuv/face/zuv-face-crop-c.jpg",
            "references/identity/zuv/face/zuv-face-crop-d.jpg",
        ]:
            imported.append(ref(rel_path, "zuv", "face_anchor"))
        imported.append(
            ref("references/identity/aachu/smiles/aachu-smile-a.jpg", "aachu", "smile")
        )
        imported.append(
            ref("references/identity/zuv/smiles/zuv-smile-a.jpg", "zuv", "smile")
        )
        imported.append(
            ref(
                "references/identity/together/face-and-body-language/together-a.jpg",
                "together",
                "together_body_language",
            )
        )
        imported.append(
            ref("references/wardrobe/aachu/aachu-wardrobe-a.jpg", "aachu", "wardrobe")
        )
        imported.append(ref("references/places/place-a.jpg", "place", "place"))
        if override_refs is not None:
            imported = override_refs

        dossier = {
            "schema_version": "2.0",
            "status": "READY_WITH_ROLE_BASED_REFERENCES",
            "last_updated": "2099-01-01",
            "selected_generation_recipe": {
                "face_visible_default": {
                    "default_aachu_close_face_anchors": [
                        "references/identity/aachu/face/aachu-face-crop-a.jpg",
                        "references/identity/aachu/face/aachu-face-crop-b.jpg",
                        "references/identity/aachu/face/aachu-face-crop-c.jpg",
                        "references/identity/aachu/face/aachu-face-crop-d.jpg",
                    ],
                    "default_zuv_close_face_anchors": [
                        "references/identity/zuv/face/zuv-face-crop-a.jpg",
                        "references/identity/zuv/face/zuv-face-crop-b.jpg",
                        "references/identity/zuv/face/zuv-face-crop-c.jpg",
                        "references/identity/zuv/face/zuv-face-crop-d.jpg",
                    ],
                    "aachu_face_identity": [
                        "references/identity/aachu/face/aachu-face-crop-a.jpg",
                        "references/identity/aachu/face/aachu-face-crop-b.jpg",
                        "references/identity/aachu/face/aachu-face-crop-c.jpg",
                        "references/identity/aachu/face/aachu-face-crop-d.jpg",
                    ],
                    "zuv_face_identity": [
                        "references/identity/zuv/face/zuv-face-crop-a.jpg",
                        "references/identity/zuv/face/zuv-face-crop-b.jpg",
                        "references/identity/zuv/face/zuv-face-crop-c.jpg",
                        "references/identity/zuv/face/zuv-face-crop-d.jpg",
                    ],
                }
            },
            "selected_generation_bundle": [
                "references/identity/aachu/face/aachu-face-crop-a.jpg",
                "references/identity/aachu/face/aachu-face-crop-b.jpg",
                "references/identity/zuv/face/zuv-face-crop-a.jpg",
                "references/identity/zuv/face/zuv-face-crop-b.jpg",
                "references/identity/together/face-and-body-language/together-a.jpg",
            ],
            "reference_images_for_generation": [
                "references/identity/_dossier/identity-face-contact-sheet.jpg",
                "references/identity/_dossier/identity-expressions-contact-sheet.jpg",
            ],
            "imported_references": imported,
        }
        dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
        return dossier_path

    def test_proof_contains_aachu_and_zuv_image_hashes(self):
        proof = self.build_proof()

        aachu_hashes = [
            ref["sha256"] for ref in proof["reference_inputs"] if ref["person"] == "aachu"
        ]
        zuv_hashes = [
            ref["sha256"] for ref in proof["reference_inputs"] if ref["person"] == "zuv"
        ]

        self.assertIn(hashlib.sha256(b"aachu crop a").hexdigest(), aachu_hashes)
        self.assertIn(hashlib.sha256(b"aachu crop b").hexdigest(), aachu_hashes)
        self.assertIn(hashlib.sha256(b"zuv crop a").hexdigest(), zuv_hashes)
        self.assertIn(hashlib.sha256(b"zuv crop b").hexdigest(), zuv_hashes)

    def test_proof_records_explicit_reference_roles(self):
        proof = self.build_proof()

        for reference in proof["reference_inputs"]:
            self.assertEqual(reference["delivery_mode"], "local_binary_input")
            self.assertEqual(reference["input_kind"], "image_file_bytes")
            self.assertTrue(reference["role"])
            self.assertNotEqual(reference["role"], "prompt text path")
            self.assertRegex(reference["sha256"], r"^[0-9a-f]{64}$")

        roles = {reference["role"] for reference in proof["reference_inputs"]}
        self.assertIn("aachu_identity_face_crop", roles)
        self.assertIn("zuv_identity_face_crop", roles)
        self.assertIn("couple_relationship_reference", roles)
        self.assertIn("style_reference", roles)

    def test_proof_includes_role_based_dossier_library(self):
        proof = self.build_proof()

        library = proof["role_based_reference_library"]

        self.assertEqual(library["status"], "pass")
        self.assertEqual(library["schema_version"], "2.0")
        self.assertEqual(library["face_anchor_counts"], {"aachu": 4, "zuv": 4})
        self.assertEqual(library["required_min_face_anchors_per_subject"], 4)

        bundle_paths = {
            ref["path"] for ref in library["default_generation_bundle_inputs"]
        }
        self.assertIn(
            "references/identity/aachu/face/aachu-face-crop-a.jpg", bundle_paths
        )
        self.assertIn(
            "references/identity/zuv/face/zuv-face-crop-a.jpg", bundle_paths
        )
        for reference in library["role_reference_inputs"]:
            self.assertEqual(reference["delivery_mode"], "local_binary_input")
            self.assertEqual(reference["input_kind"], "image_file_bytes")
            self.assertTrue(reference["use_for"])
            self.assertTrue(reference["do_not_use_for"])

    def test_role_based_dossier_blocks_support_refs_from_face_identity(self):
        proof = self.build_proof()

        library = proof["role_based_reference_library"]
        for reference in library["role_reference_inputs"]:
            if reference["role"] != "face_anchor":
                self.assertIn("face_identity", reference["do_not_use_for"])

    def test_role_based_dossier_requires_multiple_clean_face_anchors(self):
        weak_refs = [
            {
                "id": "TEST001",
                "path": "references/identity/aachu/face/aachu-face-crop-a.jpg",
                "filename": "aachu-face-crop-a.jpg",
                "subject": "aachu",
                "role": "face_anchor",
                "use_for": ["face_identity"],
                "do_not_use_for": ["place_reference"],
                "quality": "primary",
                "source_path": "/test-source/aachu-face-crop-a.jpg",
                "source_filename": "aachu-face-crop-a.jpg",
                "width": 100,
                "height": 100,
                "sha256": hashlib.sha256(b"aachu crop a").hexdigest(),
            }
        ]
        self.write_identity_dossier(override_refs=weak_refs)

        with self.assertRaisesRegex(
            pipeline.ReferenceSelectionError,
            "At least 4 clean face anchors are required for aachu and zuv",
        ):
            self.build_proof()

    def test_refuses_prompt_only_generation(self):
        with self.assertRaises(pipeline.PromptOnlyReferenceError):
            self.build_proof(reference_delivery_mode="prompt_only_paths")

    def test_marks_status_blocked_if_no_local_workflow_exists(self):
        proof = self.build_proof()

        self.assertEqual(proof["reference_delivery"]["status"], "pass")
        self.assertEqual(proof["workflow_readiness"]["status"], "blocked")
        self.assertEqual(proof["final_decision"]["status"], "blocked")
        self.assertIn("LOCAL_WORKFLOW_MISSING", proof["final_decision"]["failure_codes"])

    def test_discovery_marks_blocked_when_local_stack_is_missing(self):
        discovery = pipeline.discover_local_identity_stack(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_id="option_b_sdxl_instantid_pulid_ipadapter",
            search_roots=[],
            model_roots=[],
            comfyui_executable=None,
            server_stats=None,
        )

        self.assertEqual(discovery["status"], "blocked")
        self.assertIn("COMFYUI_MISSING", discovery["failure_codes"])
        self.assertIn("LOCAL_WORKFLOW_MISSING", discovery["failure_codes"])
        self.assertIn("LOCAL_MODELS_MISSING", discovery["failure_codes"])
        self.assertFalse(discovery["heavy_downloads_run"])
        self.assertFalse(discovery["model_execution_run"])

    def test_discovery_finds_existing_workflow_and_model_candidates(self):
        workflow = self.run_root / "local-workflows" / "identity-proof-comfyui.json"
        workflow.parent.mkdir()
        workflow.write_text("{}", encoding="utf-8")
        comfyui_root = self.repo_root / "ComfyUI"
        comfyui_root.mkdir()
        model_root = self.repo_root / "models"
        for rel_path in [
            "checkpoints/sd_xl_base_1.0.safetensors",
            "instantid/ip-adapter.bin",
            "controlnet/instantid-controlnet.safetensors",
        ]:
            path = model_root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake model marker")
        for filename in [
            "genderage.onnx",
            "2d106det.onnx",
            "1k3d68.onnx",
            "glintr100.onnx",
            "scrfd_10g_bnkps.onnx",
        ]:
            path = model_root / "insightface" / "models" / "antelopev2" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake antelope marker")

        discovery = pipeline.discover_local_identity_stack(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_id="option_b_sdxl_instantid_pulid_ipadapter",
            workflow_file="runs/2099-01-01_test-run/local-workflows/identity-proof-comfyui.json",
            search_roots=[comfyui_root],
            model_roots=[model_root],
            comfyui_executable="/usr/local/bin/comfyui",
            server_stats={"system": {"os": "test"}},
            python_modules=["torch", "aiohttp", "safetensors", "transformers"],
        )

        self.assertEqual(discovery["status"], "ready_for_creator_execution_approval")
        self.assertEqual(discovery["workflow"]["status"], "found")
        self.assertTrue(discovery["comfyui"]["available"])
        self.assertEqual(discovery["model_inventory"]["status"], "found")
        self.assertEqual(discovery["model_inventory"]["minimum_status"], "found")
        self.assertEqual(discovery["model_inventory"]["missing_minimum_roles"], [])
        self.assertEqual(
            discovery["model_inventory"]["minimum_required_models"][
                "instantid_ip_adapter"
            ]["status"],
            "found",
        )
        self.assertEqual(discovery["failure_codes"], [])

    def test_discovery_default_search_finds_run_local_comfyui_root(self):
        comfyui_root = self.run_root / "local-tools" / "ComfyUI"
        comfyui_root.mkdir(parents=True)

        discovery = pipeline.discover_local_identity_stack(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_id="option_b_sdxl_instantid_pulid_ipadapter",
            model_roots=[],
            comfyui_executable=None,
            server_stats=None,
            python_modules=[],
        )

        self.assertTrue(discovery["comfyui"]["available"])
        self.assertEqual(discovery["python_dependencies"]["status"], "missing")
        self.assertIn("COMFYUI_DEPS_MISSING", discovery["failure_codes"])
        self.assertIn(
            "runs/2099-01-01_test-run/local-tools/ComfyUI",
            discovery["comfyui"]["existing_roots"],
        )

    def test_discovery_reports_missing_sdxl_after_instantid_support_models_exist(self):
        comfyui_root = self.run_root / "local-tools" / "ComfyUI"
        models_root = comfyui_root / "models"
        for rel_path in [
            "instantid/ip-adapter.bin",
            "controlnet/instantid-controlnet.safetensors",
        ]:
            path = models_root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake model marker")
        for filename in [
            "genderage.onnx",
            "2d106det.onnx",
            "1k3d68.onnx",
            "glintr100.onnx",
            "scrfd_10g_bnkps.onnx",
        ]:
            path = models_root / "insightface" / "models" / "antelopev2" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake antelope marker")

        discovery = pipeline.discover_local_identity_stack(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_id="option_b_sdxl_instantid_pulid_ipadapter",
            model_roots=[models_root],
            comfyui_executable=None,
            server_stats=None,
            python_modules=["torch", "aiohttp", "safetensors", "transformers"],
        )

        inventory = discovery["model_inventory"]["minimum_required_models"]

        self.assertEqual(discovery["status"], "blocked")
        self.assertIn("sdxl_base_checkpoint", discovery["model_inventory"]["missing_minimum_roles"])
        self.assertEqual(inventory["instantid_ip_adapter"]["status"], "found")
        self.assertEqual(inventory["instantid_controlnet"]["status"], "found")
        self.assertEqual(inventory["insightface_antelopev2"]["status"], "found")

    def test_execution_readiness_blocks_when_previous_cpu_attempt_stalled(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            failure_code="LOCAL_CPU_EXECUTION_STALLED"
        )

        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        self.assertEqual(readiness["status"], "blocked")
        self.assertIn("LOCAL_CPU_EXECUTION_STALLED", readiness["failure_codes"])
        self.assertEqual(readiness["copied_reference_inputs"]["status"], "pass")
        self.assertEqual(readiness["workflow_binding"]["status"], "pass")
        self.assertFalse(readiness["non_final_identity_proof_allowed"])
        self.assertFalse(readiness["final_carousel_generation_allowed"])

    def test_execution_readiness_fails_if_copied_reference_is_missing(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            hardware_status={
                "mps_available": True,
                "mps_built": True,
                "cuda_available": False,
                "effective_execution_device": "mps",
            }
        )
        (
            self.run_root
            / "local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg"
        ).unlink()

        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        self.assertEqual(readiness["status"], "blocked")
        self.assertIn(
            "COMFYUI_INPUT_REFERENCE_MISSING",
            readiness["copied_reference_inputs"]["failure_codes"],
        )

    def test_execution_readiness_can_reach_creator_approval_gate(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            hardware_status={
                "mps_available": True,
                "mps_built": True,
                "cuda_available": False,
                "effective_execution_device": "mps",
            }
        )

        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        self.assertEqual(
            readiness["status"], "ready_for_creator_non_final_identity_proof_approval"
        )
        self.assertEqual(
            readiness["final_decision"]["status"],
            "pending_creator_model_execution_approval",
        )
        self.assertFalse(readiness["non_final_identity_proof_allowed"])
        self.assertFalse(readiness["final_carousel_generation_allowed"])

    def test_compute_diagnostic_blocks_cpu_only_machine(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            failure_code="LOCAL_CPU_EXECUTION_STALLED"
        )
        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        diagnostic = pipeline.build_local_compute_diagnostic(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            readiness=readiness,
            execution_report=execution_report,
            torch_probe={
                "status": "pass",
                "python": "/test/python",
                "torch_version": "2.test",
                "mps_built": True,
                "mps_available": False,
                "cuda_available": False,
                "cuda_device_count": 0,
                "selected_device": "cpu",
                "unavailable_reason": "MACOS_OR_DEVICE_NOT_MPS_ENABLED",
            },
        )

        self.assertEqual(diagnostic["status"], "blocked")
        self.assertFalse(diagnostic["local_compute_ready"])
        self.assertEqual(diagnostic["selected_execution_device"], "cpu")
        self.assertIn("LOCAL_COMPUTE_CPU_ONLY", diagnostic["failure_codes"])
        self.assertIn("LOCAL_CPU_EXECUTION_STALLED", diagnostic["failure_codes"])
        self.assertFalse(diagnostic["non_final_identity_proof_allowed"])
        self.assertFalse(diagnostic["final_carousel_generation_allowed"])

    def test_compute_diagnostic_reaches_creator_gate_on_mps(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            hardware_status={
                "mps_available": True,
                "mps_built": True,
                "cuda_available": False,
                "effective_execution_device": "mps",
            }
        )
        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        diagnostic = pipeline.build_local_compute_diagnostic(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=self.ready_discovery(),
            readiness=readiness,
            execution_report=execution_report,
            torch_probe={
                "status": "pass",
                "python": "/test/python",
                "torch_version": "2.test",
                "mps_built": True,
                "mps_available": True,
                "cuda_available": False,
                "cuda_device_count": 0,
                "selected_device": "mps",
                "unavailable_reason": None,
            },
        )

        self.assertEqual(
            diagnostic["status"], "ready_for_creator_model_execution_approval"
        )
        self.assertTrue(diagnostic["local_compute_ready"])
        self.assertEqual(diagnostic["selected_execution_device"], "mps")
        self.assertEqual(diagnostic["failure_codes"], [])
        self.assertEqual(
            diagnostic["final_decision"]["status"],
            "pending_creator_model_execution_approval",
        )
        self.assertFalse(diagnostic["non_final_identity_proof_allowed"])
        self.assertFalse(diagnostic["final_carousel_generation_allowed"])

    def test_handoff_manifest_records_complete_non_cpu_transfer_bundle(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            failure_code="LOCAL_CPU_EXECUTION_STALLED"
        )
        proof = self.build_proof(workflow_file=workflow)
        pipeline.write_proof_artifacts(self.repo_root, proof)
        discovery = {
            **self.ready_discovery(),
            "run_id": self.run_id,
            "model_inventory": {"minimum_required_models": {}},
        }
        (
            self.run_root / "evals" / pipeline.DISCOVERY_FILENAME
        ).write_text(json.dumps(discovery), encoding="utf-8")
        readiness = pipeline.build_local_identity_execution_readiness(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=discovery,
            execution_report=execution_report,
        )
        pipeline.write_execution_readiness_artifacts(self.repo_root, readiness)
        diagnostic = pipeline.build_local_compute_diagnostic(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            discovery=discovery,
            readiness=readiness,
            execution_report=execution_report,
            torch_probe={
                "status": "pass",
                "python": "/test/python",
                "torch_version": "2.test",
                "mps_built": True,
                "mps_available": False,
                "cuda_available": False,
                "cuda_device_count": 0,
                "selected_device": "cpu",
                "unavailable_reason": "MACOS_OR_DEVICE_NOT_MPS_ENABLED",
            },
        )
        pipeline.write_compute_diagnostic_artifacts(self.repo_root, diagnostic)

        manifest = pipeline.build_local_identity_handoff_manifest(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            diagnostic=diagnostic,
            discovery=discovery,
            execution_report=execution_report,
        )
        manifest_path, report_path = pipeline.write_handoff_artifacts(
            self.repo_root, manifest
        )

        self.assertEqual(manifest["status"], "ready_for_non_cpu_handoff")
        self.assertEqual(manifest["missing_required_files"], [])
        records = {record["role"]: record for record in manifest["files"]}
        for role in [
            "workflow",
            "selected_reference_manifest",
            "local_reference_proof",
            "local_stack_discovery",
            "local_execution_readiness",
            "local_compute_diagnostic",
            "aachu_face_anchor",
            "zuv_face_anchor",
            "together_pose_context",
        ]:
            self.assertEqual(records[role]["status"], "pass")
            self.assertRegex(records[role]["sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(
            manifest["target_requirements"]["torch_mps_available_or_cuda_available"]
        )
        self.assertFalse(manifest["target_requirements"]["cpu_allowed"])
        self.assertTrue(manifest_path.exists())
        self.assertIn("Do not run this proof on CPU", report_path.read_text())

    def test_handoff_manifest_blocks_when_required_bundle_files_are_missing(self):
        workflow, execution_report = self.write_identity_proof_runtime_files(
            failure_code="LOCAL_CPU_EXECUTION_STALLED"
        )
        diagnostic = {
            "status": "blocked",
            "failure_codes": ["LOCAL_COMPUTE_CPU_ONLY"],
            "selected_execution_device": "cpu",
        }

        manifest = pipeline.build_local_identity_handoff_manifest(
            repo_root=self.repo_root,
            run_id=self.run_id,
            workflow_file=workflow,
            diagnostic=diagnostic,
            discovery=self.ready_discovery(),
            execution_report=execution_report,
        )

        self.assertEqual(manifest["status"], "blocked")
        self.assertIn(
            f"runs/{self.run_id}/evals/local_identity_reference_proof.json",
            manifest["missing_required_files"],
        )
        self.assertIn(
            f"runs/{self.run_id}/evals/local_compute_diagnostic.json",
            manifest["missing_required_files"],
        )


if __name__ == "__main__":
    unittest.main()
