# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from unittest.mock import patch

import pytest

from aws_cli_migrate.cli import main


class TestCLI:
    """Test cases for CLI interface."""

    def test_script_not_found(self, capsys):
        """Test error when script file doesn't exist."""
        with patch("sys.argv", ["migrate-aws-cli", "--script", "nonexistent.sh"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_fix_and_output_conflict(self, capsys):
        """Test error when both --fix and --output are provided."""
        with patch(
            "sys.argv", ["migrate-aws-cli", "--script", "test.sh", "--fix", "--output", "out.sh"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_fix_and_interactive_conflict(self, capsys):
        """Test error when both --fix and --interactive are provided."""
        with patch(
            "sys.argv", ["migrate-aws-cli", "--script", "test.sh", "--fix", "--interactive"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_no_issues_found(self, tmp_path, capsys):
        """Test output when no issues are found."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("echo 'hello world'")

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file)]):
            main()
            captured = capsys.readouterr()
            assert "No issues found" in captured.out

    def test_dry_run_mode(self, tmp_path, capsys):
        """Test dry run mode displays findings."""
        script_file = tmp_path / "test.sh"
        script_file.write_text(
            "aws secretsmanager put-secret-value --secret-id secret1213 --secret-binary file://data.json"
        )

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file)]):
            main()
            captured = capsys.readouterr()
            assert "Found" in captured.out
            assert "issue" in captured.out

    def test_fix_mode_only_manual_fixes(self, tmp_path, capsys):
        """Test fix mode with only manual fixes."""
        script_file = tmp_path / "test.sh"
        original_script_content = "aws s3 cp s3://my-bucket ."
        script_file.write_text(original_script_content)

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file), "--fix"]):
            main()
            fixed_content = script_file.read_text()
            captured = capsys.readouterr()
            # Script should remain unchanged.
            assert fixed_content == original_script_content

            # Display total number of issues.
            assert "Found 2 issue(s)." in captured.out

            # Should show manual review section
            assert "2 issue(s) require manual review" in captured.out
            assert "MANUAL REVIEW REQUIRED" in captured.out
            assert "This issue requires manual intervention" in captured.out

    def test_fix_mode_with_manual_review(self, tmp_path, capsys):
        """Test fix mode displays manual review findings after applying fixes."""
        script_file = tmp_path / "test.sh"
        script_file.write_text(
            "aws secretsmanager put-secret-value --secret-id secret1213 --secret-binary file://data.json\n"
            "aws ecr get-login --region us-west-2\n"
            "aws s3 cp s3://my-bucket s3://my-bucket2"
        )

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file), "--fix"]):
            main()
            captured = capsys.readouterr()

            # Should show fix was applied
            assert f"Applied 1 fix(es) to: {str(tmp_path)}" in captured.out

            # Should show manual review section
            assert "5 issue(s) require manual review" in captured.out
            assert "MANUAL REVIEW REQUIRED" in captured.out
            assert "This issue requires manual intervention" in captured.out

            # Script should have auto-fixes applied but manual review command unchanged
            fixed_content = script_file.read_text()
            assert "--copy-props none" in fixed_content
            assert "aws ecr get-login" in fixed_content
            assert (
                "aws secretsmanager put-secret-value --secret-id secret1213 "
                "--secret-binary file://data.json\n" in fixed_content
            )

    def test_fix_mode_no_issues_found(self, tmp_path, capsys):
        """Test fix mode when no issues are found."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("echo 'foobar'")

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file), "--fix"]):
            main()
            fixed_content = script_file.read_text()
            captured_out = capsys.readouterr()
            assert fixed_content == "echo 'foobar'"
            assert "No issues found" in captured_out.out

    def test_fix_mode_hidden_aliases(self, tmp_path, capsys):
        """Test fix mode in the case of using hidden aliases in two different commands."""
        script_file = tmp_path / "test.sh"
        script_file.write_text(
            "aws lambda publish-version --function-name myfunction --code-sha256 abc123\n"
            "aws deploy create-deployment-group --application-name myapp "
            "--deployment-group-name mygroup --ec-2-tag-set file://tags.json"
        )

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file), "--fix"]):
            main()
            captured = capsys.readouterr()

            # Should show fix was applied
            assert f"Applied 1 fix(es) to: {str(tmp_path)}" in captured.out
            # The number of lines should remain the same after applying fixes
            assert len(script_file.read_text().splitlines()) == 2

            # Should show manual review section
            assert "4 issue(s) require manual review" in captured.out
            assert "MANUAL REVIEW REQUIRED" in captured.out
            assert "This issue requires manual intervention" in captured.out
            assert captured.out.count("binary-params-base64 [MANUAL REVIEW REQUIRED]") == 2
            assert captured.out.count("pager-by-default [MANUAL REVIEW REQUIRED]") == 2

            # The hidden alias must not be present in the modified script
            assert "--ec-2-tag-set" not in script_file.read_text()

    def test_output_mode(self, tmp_path):
        """Test output mode creates new file."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text("aws s3 cp s3://my-bucket s3://my-bucket2")

        with patch(
            "sys.argv",
            ["migrate-aws-cli", "--script", str(script_file), "--output", str(output_file)],
        ):
            main()
            assert output_file.exists()
            content = output_file.read_text()
            # 1 command, 1 applicable rule = 1 flag added
            assert "--copy-props none" in content

    def test_interactive_mode_accept_all(self, tmp_path):
        """Test interactive mode with 'y' to accept all changes, and "n" to proceed through
        all manual-review issues.
        """
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws deploy create-deployment-group --application-name myapp "
            "--deployment-group-name mygroup --ec-2-tag-set file://tags.json\n"
            "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive\n"
            "aws cloudformation deploy"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", side_effect=["y", "y", "y", "n", "n", "n", "n", "n", "n"]):
                main()
                fixed_content = output_file.read_text()
                # 3 commands, 1 applicable rule each = 3 findings
                assert fixed_content.count("--ec2-tag-set") == 1
                assert fixed_content.count("--copy-props none") == 1
                assert fixed_content.count("--fail-on-empty-changeset") == 1

    def test_interactive_mode_reject_all(self, tmp_path, capsys):
        """Test interactive mode with 'n' to reject all changes."""
        script_file = tmp_path / "test.sh"
        original = "aws secretsmanager put-secret-value --secret-id secret1213 --secret-binary file://data.json"
        script_file.write_text(original)

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file), "--interactive"]):
            with patch("builtins.input", return_value="n"):
                main()
                captured = capsys.readouterr()
                assert "No changes were accepted" in captured.out

    def test_interactive_mode_update_all(self, tmp_path):
        """Test interactive mode with 'u' to accept remaining changes."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws deploy create-deployment-group --application-name myapp "
            "--deployment-group-name mygroup --ec-2-tag-set file://tags.json\n"
            "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", return_value="u"):
                main()
                fixed_content = output_file.read_text()
                # 2 commands, 1 applicable rule each = 2 findings.
                assert fixed_content.count("--ec2-tag-set") == 1
                assert fixed_content.count("--ec-2-tag-set") == 0
                assert fixed_content.count("--copy-props none") == 1

    def test_interactive_mode_update_all_summarizes_unseen_manual_issues(self, tmp_path, capsys):
        """Test interactive mode with 'u' summarizes issues that are not auto-fixable that were
        not encountered in interactive mode.
        """
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive\naws ecr get-login"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", return_value="u"):
                main()
                fixed_content = output_file.read_text()
                captured = capsys.readouterr()
                assert fixed_content.count("--copy-props none") == 1
                assert "️3 issue(s) require manual review:" in captured.out

    def test_interactive_mode_save_and_exit(self, tmp_path):
        """Test interactive mode with 's' to save and exit."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text("aws cloudformation deploy\naws cloudformation deploy")

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", side_effect=["y", "s"]):
                main()
                fixed_content = output_file.read_text()
                # Only first change should be applied since we pressed 's' on the second finding.
                # First finding is deploy-empty-changeset for the first command.
                assert fixed_content.count("--fail-on-empty-changeset") == 1

    def test_interactive_mode_quit(self, tmp_path):
        """Test interactive mode with 'q' to quit without saving."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws secretsmanager put-secret-value --secret-id secret1213 --secret-binary file://data.json"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", return_value="q"):
                main()
                # Output file should not exist since we quit without saving
                assert not output_file.exists()

    def test_dry_run_mode_with_manual_review(self, tmp_path, capsys):
        """Test dry run mode displays manual review findings."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("aws ecr get-login --region us-west-2")

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file)]):
            main()
            captured = capsys.readouterr()
            assert "MANUAL REVIEW REQUIRED" in captured.out
            assert "This issue requires manual intervention" in captured.out
            assert "get-login-password" in captured.out

    def test_interactive_mode_with_manual_review(self, tmp_path, capsys):
        """Test interactive mode handles manual review findings."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive\n"
            "aws cloudformation deploy\n"
            "aws ecr get-login --region us-west-2"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            # Accept first two auto-fixable findings, then 'n' for manual review finding
            with patch("builtins.input", side_effect=["y", "y", "n", "n", "n", "n", "n"]):
                main()
                captured = capsys.readouterr()

                # Should display manual review finding
                assert "MANUAL REVIEW REQUIRED" in captured.out
                assert "This issue requires manual intervention" in captured.out

                # Output should have auto-fixes but not manual review changes
                fixed_content = output_file.read_text()
                assert fixed_content == (
                    "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive --copy-props none\n"
                    "aws cloudformation deploy --fail-on-empty-changeset\n"
                    "aws ecr get-login --region us-west-2"
                )

    def test_interactive_mode_manual_review_save_and_exit(self, tmp_path):
        """Test interactive mode with 's' on manual review finding."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive\n"
            "aws ecr get-login --region us-west-2\n"
            "aws cloudformation deploy"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            # Accept all 2 auto-fixable findings, then 's' on manual review finding (3rd)
            # This should save and exit without processing any remaining findings
            with patch("builtins.input", side_effect=["y", "y", "s"]):
                main()

                fixed_content = output_file.read_text()

                # Output should have all auto-fixes applied, and manual-review command
                # should be left unchanged.
                assert fixed_content == (
                    "aws s3 cp s3://my-bucket s3://my-bucket2 --recursive --copy-props none\n"
                    "aws ecr get-login --region us-west-2\n"
                    "aws cloudformation deploy --fail-on-empty-changeset"
                )

                # Should have saved and exited
                assert output_file.exists()

    def test_version_flag(self, capsys):
        """Test --version flag displays version and exits."""
        with patch("sys.argv", ["migrate-aws-cli", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "migrate-aws-cli" in captured.out

    def test_version_flag_short(self, capsys):
        """Test -v flag displays version and exits."""
        with patch("sys.argv", ["migrate-aws-cli", "-v"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "migrate-aws-cli" in captured.out

    def test_non_aws_command_not_matched(self, tmp_path, capsys):
        """Test that commands like 'myaws' are not matched as AWS CLI commands."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("'myaws' s3 ls")

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file)]):
            main()
            captured = capsys.readouterr()
            assert "No issues found" in captured.out

    def test_quoted_aws_command_matched(self, tmp_path, capsys):
        """Test that 'aws' in single quotes is correctly matched."""
        script_file = tmp_path / "test.sh"
        script_file.write_text(
            "'aws' secretsmanager put-secret-value --secret-id secret1213 --secret-binary file://data.json"
        )

        with patch("sys.argv", ["migrate-aws-cli", "--script", str(script_file)]):
            main()
            captured = capsys.readouterr()
            # Should find issues since 'aws' is a valid AWS CLI command
            assert "Found 2 issue" in captured.out

    def test_interactive_mode_accept_then_update_all(self, tmp_path, capsys):
        """Test interactive mode with user manually accepting a finding then auto-updating all."""
        script_file = tmp_path / "test.sh"
        output_file = tmp_path / "output.sh"
        script_file.write_text(
            "aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/file.txt\n"
            "aws cloudformation deploy\n"
            "aws s3 ls s3://my-bucket"
        )

        with patch(
            "sys.argv",
            [
                "migrate-aws-cli",
                "--script",
                str(script_file),
                "--interactive",
                "--output",
                str(output_file),
            ],
        ):
            with patch("builtins.input", side_effect=["y", "u"]):
                main()
                fixed_content = output_file.read_text()
                captured = capsys.readouterr()
                assert fixed_content == (
                    "aws s3 cp s3://mybucket/file.txt s3://mybucket2/file.txt --copy-props none\n"
                    "aws cloudformation deploy --fail-on-empty-changeset\n"
                    "aws s3 ls s3://my-bucket"
                )
                assert "Found 8 issue" in captured.out
