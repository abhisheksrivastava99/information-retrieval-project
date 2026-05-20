import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from business_review_tool.data import default_business_path, default_review_path, load_and_prepare
from business_review_tool.dataset_fetcher import (
    DatasetFetchError,
    fetch_dataset,
    is_lfs_pointer_file,
)


BUSINESS_HEADER = "business_id,name,city,categories,stars,review_count\n"
REVIEW_HEADER = "review_id,business_id,stars,text,date\n"


def write_business_csv(path: Path, name: str) -> None:
    path.write_text(
        BUSINESS_HEADER + f"b1,{name},Santa Barbara,Restaurants,4.5,10\n",
        encoding="utf-8",
    )


def write_review_csv(path: Path, text: str) -> None:
    path.write_text(
        REVIEW_HEADER + f'r1,b1,5,"{text}",2024-01-01\n',
        encoding="utf-8",
    )


class DatasetDiscoveryTests(unittest.TestCase):
    def test_default_paths_prefer_data_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            data_dir = project_dir / "data"
            data_dir.mkdir()

            root_business = project_dir / "businesses_root.csv"
            root_review = project_dir / "reviews_root.csv"
            data_business = data_dir / "businesses_data.csv"
            data_review = data_dir / "reviews_data.csv"

            write_business_csv(root_business, "Root Business")
            write_review_csv(root_review, "Root review")
            write_business_csv(data_business, "Data Business")
            write_review_csv(data_review, "Data review")

            previous_cwd = Path.cwd()
            os.chdir(project_dir)
            try:
                self.assertEqual(default_business_path().resolve(), data_business.resolve())
                self.assertEqual(default_review_path().resolve(), data_review.resolve())
            finally:
                os.chdir(previous_cwd)

    def test_explicit_paths_override_default_discovery(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            data_dir = project_dir / "data"
            data_dir.mkdir()

            explicit_business = project_dir / "businesses_explicit.csv"
            explicit_review = project_dir / "reviews_explicit.csv"
            write_business_csv(explicit_business, "Explicit Business")
            write_review_csv(explicit_review, "Explicit review")

            write_business_csv(data_dir / "businesses_data.csv", "Default Business")
            write_review_csv(data_dir / "reviews_data.csv", "Default review")

            previous_cwd = Path.cwd()
            os.chdir(project_dir)
            try:
                businesses, reviews = load_and_prepare(explicit_business, explicit_review)
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(businesses.iloc[0]["name"], "Explicit Business")
            self.assertEqual(reviews.iloc[0]["text"], "Explicit review")


class DatasetFetchTests(unittest.TestCase):
    def test_fetch_data_skips_download_when_files_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            data_dir = project_dir / "data"
            data_dir.mkdir()

            write_business_csv(data_dir / "businesses_CA(Sheet1).csv", "Existing Business")
            write_review_csv(data_dir / "reviews_CA(Sheet1).csv", "Existing review")

            with patch("business_review_tool.dataset_fetcher.ensure_git_tools") as ensure_tools:
                with patch(
                    "business_review_tool.dataset_fetcher.clone_dataset_branch"
                ) as clone_branch:
                    result = fetch_dataset(project_dir=project_dir)

            self.assertTrue(result.reused_existing)
            ensure_tools.assert_not_called()
            clone_branch.assert_not_called()

    def test_fetch_data_force_refreshes_existing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            data_dir = project_dir / "data"
            data_dir.mkdir()

            business_path = data_dir / "businesses_CA(Sheet1).csv"
            review_path = data_dir / "reviews_CA(Sheet1).csv"
            write_business_csv(business_path, "Old Business")
            write_review_csv(review_path, "Old review")

            def fake_clone(destination: Path) -> None:
                remote_data_dir = destination / "data"
                remote_data_dir.mkdir(parents=True)
                write_business_csv(remote_data_dir / "businesses_CA(Sheet1).csv", "Fresh Business")
                write_review_csv(remote_data_dir / "reviews_CA(Sheet1).csv", "Fresh review")

            with patch("business_review_tool.dataset_fetcher.ensure_git_tools"):
                with patch(
                    "business_review_tool.dataset_fetcher.clone_dataset_branch",
                    side_effect=fake_clone,
                ):
                    result = fetch_dataset(force=True, project_dir=project_dir)

            self.assertFalse(result.reused_existing)
            self.assertIn("Fresh Business", business_path.read_text(encoding="utf-8"))
            self.assertIn("Fresh review", review_path.read_text(encoding="utf-8"))

    def test_lfs_pointer_files_raise_clear_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            pointer_text = (
                "version https://git-lfs.github.com/spec/v1\n"
                "oid sha256:1234567890abcdef\n"
                "size 123\n"
            )

            def fake_clone(destination: Path) -> None:
                remote_data_dir = destination / "data"
                remote_data_dir.mkdir(parents=True)
                (remote_data_dir / "businesses_CA(Sheet1).csv").write_text(
                    pointer_text,
                    encoding="utf-8",
                )
                write_review_csv(remote_data_dir / "reviews_CA(Sheet1).csv", "Fresh review")

            with patch("business_review_tool.dataset_fetcher.ensure_git_tools"):
                with patch(
                    "business_review_tool.dataset_fetcher.clone_dataset_branch",
                    side_effect=fake_clone,
                ):
                    with self.assertRaises(DatasetFetchError) as context:
                        fetch_dataset(force=True, project_dir=project_dir)

            self.assertIn("pointer file", str(context.exception))

    def test_pointer_detection_identifies_lfs_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "pointer.csv"
            file_path.write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                "oid sha256:abcdef\n"
                "size 42\n",
                encoding="utf-8",
            )
            self.assertTrue(is_lfs_pointer_file(file_path))


if __name__ == "__main__":
    unittest.main()
