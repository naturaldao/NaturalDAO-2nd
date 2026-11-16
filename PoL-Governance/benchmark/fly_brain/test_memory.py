"""Mechanism checks; run with unittest discover -s this directory."""
import unittest
import numpy as np
import memory_experiment as m


class MemoryMechanismTests(unittest.TestCase):
    def test_same_future_inputs_contraction(self):
        w, inputs = m.load_graph()
        w, _ = m.topology(w, "flyvis_template", np.random.default_rng(1))
        rng = np.random.default_rng(2)
        h1, h2 = rng.uniform(-1, 1, (2, 65))
        encoding = rng.normal(size=(65, 2))
        initial = np.max(np.abs(h1-h2))
        for t in range(1, 21):
            cue = rng.normal(size=(1, 2))
            h1 = m.step(h1[None, :], cue, w, encoding)[0]
            h2 = m.step(h2[None, :], cue, w, encoding)[0]
            self.assertLessEqual(np.max(np.abs(h1-h2)), initial*0.94**t + 1e-12)

    def test_rewire_preserves_signed_degrees_and_original_loops(self):
        w, _ = m.load_graph()
        rewired, count = m.topology(w, "degree_rewired", np.random.default_rng(7))
        self.assertEqual(int(np.count_nonzero(np.diag(w))), 24)
        self.assertGreater(count, 500)
        np.testing.assert_array_equal(m.signed_degrees(w), m.signed_degrees(rewired))
        np.testing.assert_array_equal(np.diag(w) != 0, np.diag(rewired) != 0)
        self.assertGreater(np.count_nonzero((w != 0) != (rewired != 0)), 100)

    def test_no_event_gate_leaves_state_and_random_change_has_matched_norm(self):
        rng = np.random.default_rng(8)
        h = rng.normal(size=(16, 65))
        a = rng.normal(size=65)
        dual = a / (a @ a)
        random_unit = rng.normal(size=h.shape)
        random_unit /= np.linalg.norm(random_unit, axis=1, keepdims=True)
        np.testing.assert_array_equal(m.intervene(h, "output_gate", a, dual, random_unit), h)
        selective = m.intervene(h, "selective", a, dual, random_unit)
        random = m.intervene(h, "random_matched", a, dual, random_unit)
        np.testing.assert_allclose(np.linalg.norm(h-selective, axis=1), np.linalg.norm(h-random, axis=1))

    def test_reset_removes_input_information_under_independent_observation_noise(self):
        rng = np.random.default_rng(11)
        y_train, y_eval = rng.normal(size=(2, 1024, 2))
        x_train = rng.normal(0, m.NOISE, (1024, 65))
        x_eval = rng.normal(0, m.NOISE, (1024, 65))
        predicted = m.predict(m.fit(x_train, y_train), x_eval)
        self.assertLess(m.r2(y_eval[:, 0], predicted[:, 0]), 0.1)


if __name__ == "__main__":
    unittest.main()
