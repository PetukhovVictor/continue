
from nose.tools import eq_
import itertools
import math

from libctw import ctw, naive_ctw
from libctw.formatting import to_bits


def test_kt_estim_update():
    _check_estim_update(ctw._kt_estim_update, naive_ctw._estim_kt_p)


def test_determ_estim_update():
    _check_estim_update(ctw._determ_estim_update, naive_ctw._estim_determ_p)


def test_empty_context():
    model = ctw.create_model()
    eq_(model.predict_one(), 0.5)


def _get_history_p(model):
    return math.exp(model.get_history_log_p())


def test_see():
    contexted =naive_ctw._Contexted(naive_ctw._estim_kt_p)
    for seq in iter_all_seqs(seq_len=10):
        model = ctw.create_model()
        model.see_generated(to_bits(seq))
        eq_float_(_get_history_p(model), contexted.calc_p("", seq))


def test_predict_first():
    for determ in [False, True]:
        model = ctw.create_model(determ)
        verifier = naive_ctw.create_model(determ)
        eq_float_(model.predict_one(), verifier.predict_one())


def test_predict_one():
    seq_len = 8
    for determ in [False, True]:
        for seq in iter_all_seqs(seq_len):
            model = ctw.create_model(determ)
            verifier = naive_ctw.create_model(determ)
            for c in seq:
                model.see_generated(to_bits(c))
                verifier.see_generated(to_bits(c))
                eq_float_(model.predict_one(), verifier.predict_one(),
                        precision=10)


def test_max_depth():
    model = ctw.create_model(max_depth=0)
    eq_(_get_history_p(model), 1.0)
    model.see_generated([1])
    eq_(model.root.log_p_estim, math.log(0.5))
    eq_(model.root.log_pw, model.root.log_p_estim)

    model.see_generated([1])
    eq_(_get_history_p(model), naive_ctw._estim_kt_p(0, 2))


def test_max_depth_sum():
    for seq_len in range(10):
        total = 0.0
        for seq in iter_all_seqs(seq_len):
            model = ctw.create_model(max_depth=8)
            model.see_generated(to_bits(seq))
            total += _get_history_p(model)

        eq_float_(total, 1.0, precision=15)


def test_max_depth_example():
    # The calculated probablities are from the
    # 'Reflections on "The Context-Tree Weighting Method: Basic Properties"'
    # paper (figure 6 and 7).
    model = ctw.create_model(max_depth=3)
    model.see_added([1,1,0])
    model.see_generated(to_bits("0100110"))
    p_seq = _get_history_p(model)
    eq_float_(p_seq, 7/2048.0)

    model.see_generated([0])
    p_seq2 = _get_history_p(model)
    eq_float_(p_seq2, 153/65536.0)


def test_manual_example():
    model = ctw.create_model()
    model.see_generated([1])
    eq_(_get_history_p(model), 0.5)
    model.see_generated([1])
    # pw = 0.5 * (3/8 + 1 * 0.5 * 0.5) = 5/16.0
    eq_float_(_get_history_p(model), 5/16.0)


def test_continue_example():
    # A test of the documentation example:
    # ./continue.py -n 10 01101
    model = ctw.create_model()
    model.see_generated(to_bits("01101"))
    p_given = _get_history_p(model)
    model.see_generated(to_bits("1011011011"))
    p_seq = _get_history_p(model)
    eq_float_(p_seq/float(p_given), 0.052825, precision=6)


def iter_all_seqs(seq_len):
    for seq in itertools.product(["0", "1"], repeat=seq_len):
        yield "".join(seq)


def _check_estim_update(estim_update, estimator):
    for seq_len in range(10):
        for bits in itertools.product([0, 1], repeat=seq_len):
            p = 1.0
            counts = [0, 0]
            for bit in bits:
                p *= math.exp(estim_update(bit, counts))
                counts[bit] += 1

            eq_float_(p, estimator(*counts))


def eq_float_(value, expected, precision=13):
    eq_("%.*f" % (precision, value),
            "%.*f" % (precision, expected))
