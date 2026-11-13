"""Check pinned downloads and the jumpbox instructions without downloading binaries."""

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DownloadsTest(unittest.TestCase):
    def test_release_pins_and_extraction_names(self):
        jumpbox = (ROOT / "docs/02-jumpbox.md").read_text()
        for arch in ("amd64", "arm64"):
            with self.subTest(arch=arch):
                urls = (ROOT / f"downloads-{arch}.txt").read_text().splitlines()
                expected = [
                    f"https://dl.k8s.io/v1.37.2/bin/linux/{arch}/{binary}"
                    for binary in (
                        "kubectl", "kube-apiserver", "kube-controller-manager",
                        "kube-scheduler", "kube-proxy", "kubelet",
                    )
                ]
                for repo, version, name in (
                    ("kubernetes-sigs/cri-tools", "1.37.0", f"crictl-v1.37.0-linux-{arch}.tar.gz"),
                    ("opencontainers/runc", "1.5.3", f"runc.{arch}"),
                    ("containernetworking/plugins", "1.10.0", f"cni-plugins-linux-{arch}-v1.10.0.tgz"),
                    ("containerd/containerd", "2.4.2", f"containerd-2.4.2-linux-{arch}.tar.gz"),
                    ("etcd-io/etcd", "3.7.3", f"etcd-v3.7.3-linux-{arch}.tar.gz"),
                ):
                    expected.append(f"https://github.com/{repo}/releases/download/v{version}/{name}")
                self.assertEqual(urls, expected)
                archives = re.findall(r"tar -xvf downloads/(\S+)", jumpbox)
                self.assertEqual(len(archives), 4)
                for archive in archives:
                    self.assertIn(archive.replace("${ARCH}", arch), [url.rsplit("/", 1)[1] for url in urls])
                for member in ("etcdctl", "etcd"):
                    self.assertIn(f"etcd-v3.7.3-linux-${{ARCH}}/{member}", jumpbox)

    def test_fork_and_documented_versions(self):
        self.assertIn("https://github.com/ncode/kubernetes-the-hard-way.git",
                      (ROOT / "docs/02-jumpbox.md").read_text())
        for path in (ROOT / "docs").glob("*.md"):
            self.assertNotRegex(path.read_text(), r"v1\.32\.3|v1\.32\.0|2\.1\.0-beta\.0|v1\.6\.2|v3\.6\.0-rc\.3")
        readme = (ROOT / "README.md").read_text()
        for version in ("v1.37.2", "v1.37.0", "v2.4.2", "v1.5.3", "v1.10.0", "v3.7.3"):
            self.assertIn(version, readme)

    def test_version_output_examples(self):
        for name in ("08-bootstrapping-kubernetes-controllers.md", "10-configuring-kubectl.md"):
            self.assertIn('"minor": "37"', (ROOT / "docs" / name).read_text())
        for name in ("02-jumpbox.md", "10-configuring-kubectl.md"):
            self.assertIn("Kustomize Version: v5.8.1", (ROOT / "docs" / name).read_text())


if __name__ == "__main__":
    unittest.main()
