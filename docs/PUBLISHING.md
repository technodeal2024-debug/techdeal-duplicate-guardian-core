# Public OSS release checklist

Repository visibility is already PUBLIC. The commercial Android and Windows applications remain private and separate.

Before tagging a release:
1. Recheck rights-holder permission, copyright attribution, third-party licensing and complete Git history for secrets or personal data.
2. Preserve offline, read-only operation. Review symlinks, adversarial path races, file mutation handling and permissions.
3. Confirm green GitHub Actions on the exact release commit across Windows, Linux and macOS. CI is not a security certification.
4. Check version, README, CHANGELOG, examples, security policy and known limitations.
5. Obtain maintainer approval, create a version tag and publish accurate release notes.
6. Verify the public release anonymously and maintain issues/PRs for actual user needs.

Never fabricate stars, downloads, forks, adoption, grant decisions or external contributors.
Codex for OSS review is independent of this repository; a public repo alone does not guarantee an award.
