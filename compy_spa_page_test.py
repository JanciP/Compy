"""Serving the built react pages: a missing frontend/dist (fresh checkout,
or a dev who opened Flask's port instead of the Vite dev server) must give
a readable hint instead of a FileNotFoundError traceback."""
import os
import tempfile
import unittest

import compy_testing


class TestSpaPages(compy_testing.CompyServerTestCase):

    def setUp(self):
        super().setUp()
        self.session = self.adminSession()

    def withDistDir(self, dist_dir):
        """Point the running app at another dist directory for one test."""
        flask_obj = self.app.extensions['compy_flask']
        previous = flask_obj.dist_dir_
        flask_obj.dist_dir_ = dist_dir
        self.addCleanup(setattr, flask_obj, 'dist_dir_', previous)

    def testMissingBundleExplainsHowToBuildOrUseVite(self):
        with tempfile.TemporaryDirectory() as empty:
            self.withDistDir(empty)
            reply = self.session.get(self.base_url + "/admin")
        self.assertEqual(reply.status_code, 503)
        self.assertIn("Frontend not built", reply.text)
        self.assertIn("npm --prefix frontend run build", reply.text)
        self.assertIn("http://localhost:5173/app/admin.html", reply.text)

    def testBuiltBundleIsServed(self):
        with tempfile.TemporaryDirectory() as dist:
            with open(os.path.join(dist, "admin.html"), "w") as page:
                page.write("<!doctype html><title>compy admin</title>")
            self.withDistDir(dist)
            reply = self.session.get(self.base_url + "/admin")
            self.assertEqual(reply.status_code, 200)
            self.assertIn("compy admin", reply.text)


if __name__ == '__main__':
    unittest.main()
