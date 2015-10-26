import unittest
from mock import MagicMock
from mock import Mock
import httpretty
from bluegreen import BlueGreen

class TestBlueGreen(unittest.TestCase):

  def setUp(self):
    config = {'name': 'test-app', 'hooks': {'before_pre': 'echo test', 'after_swap': 'undefined_command'}}

    self.bg = BlueGreen('token', 'tsuru.globoi.com', config)
    self.cnames = [u'cname1', u'cname2']

  @httpretty.activate
  def test_get_cname_returns_a_list_when_present(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                           body='{"cname":["cname1", "cname2"]}')

    self.assertEqual(self.bg.get_cname('xpto'), self.cnames)

  @httpretty.activate
  def test_get_cname_returns_none_when_empty(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                           body='{"cname":[]}')

    self.assertIsNone(self.bg.get_cname('xpto'))

  @httpretty.activate
  def test_remove_cname_return_true_when_can_remove(self):
    httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/cname',
                           data='{"cname":["cname1", "cname2"]}',
                           status=200)

    self.assertTrue(self.bg.remove_cname('xpto', self.cnames))

  @httpretty.activate
  def test_remove_cname_return_false_when_cant_remove(self):
    httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/cname',
                           data='{"cname":["cname1", "cname2"]}',
                           status=500)

    self.assertFalse(self.bg.remove_cname('xpto', self.cnames))

  @httpretty.activate
  def test_set_cname_return_true_when_can_set(self):
    httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/cname',
                           data='{"cname":["cname1", "cname2"]}',
                           status=200)

    self.assertTrue(self.bg.set_cname('xpto', self.cnames))

  @httpretty.activate
  def test_set_cname_return_false_when_cant_set(self):
    httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/cname',
                           data='{"cname":["cname1", "cname2"]}',
                           status=500)

    self.assertFalse(self.bg.set_cname('xpto', self.cnames))

  @httpretty.activate
  def test_env_set_return_true_when_can_set(self):
    httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/env',
                           data='{"TAG":"tag_value"}',
                           status=200)

    self.assertTrue(self.bg.env_set('xpto', 'TAG', 'tag_value'))

  @httpretty.activate
  def test_env_set_return_false_when_cant_set(self):
    httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/env',
                           data='{"TAG":"tag_value"}',
                           status=500)

    self.assertFalse(self.bg.env_set('xpto', 'TAG', 'tag_value'))

  @httpretty.activate
  def test_env_get_returns_a_value_when_present(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto/env',
                           data='["TAG"]',
                           body='[{"name":"TAG","public":true,"value":"1.0"}]')

    self.assertEqual(self.bg.env_get('xpto', 'TAG'), '1.0')

  @httpretty.activate
  def test_env_get_returns_none_when_null(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto/env',
                           data='["TAG"]',
                           body='null')

    self.assertIsNone(self.bg.env_get('xpto', 'TAG'))

  @httpretty.activate
  def test_env_get_returns_none_when_null(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto/env',
                           data='["TAG"]',
                           body='[]')

    self.assertIsNone(self.bg.env_get('xpto', 'TAG'))

  @httpretty.activate
  def test_total_units_zero_when_empty(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                           body='{"units":[]}',
                           status=500)

    self.assertEqual(self.bg.total_units('xpto'), 0)

  @httpretty.activate
  def test_total_units_gt_zero_when_not_empty(self):
    httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                           body='{"units":["unit1"]}',
                           status=500)

    self.assertGreater(self.bg.total_units('xpto'), 0)

  @httpretty.activate
  def test_remove_units_should_return_true_when_removes(self):
    self.bg.total_units = Mock(side_effect=self.mock_total_units([2, 1]))

    httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/units',
                           data='1',
                           status=200)

    self.assertTrue(self.bg.remove_units('xpto'))
    self.assertEqual({"units": ["1"]}, httpretty.last_request().querystring)

  @httpretty.activate
  def test_remove_units_should_return_false_when_not_removes(self):
    self.bg.total_units = MagicMock(return_value=2)

    httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/units',
                           data='1',
                           status=500)

    self.assertFalse(self.bg.remove_units('xpto'))

  @httpretty.activate
  def test_add_units_should_return_true_when_adds(self):
    self.bg.total_units = MagicMock(side_effect=self.mock_total_units([1, 2]))

    httpretty.register_uri(httpretty.PUT, 'http://tsuru.globoi.com/apps/xpto/units?units=1',
                           data='1',
                           status=200)

    self.assertTrue(self.bg.add_units('xpto', 2))
    self.assertEqual({"units": ["1"]}, httpretty.last_request().querystring)

  @httpretty.activate
  def test_add_units_should_return_false_when_adds(self):
    self.bg.total_units = MagicMock(return_value=1)

    httpretty.register_uri(httpretty.PUT, 'http://tsuru.globoi.com/apps/xpto/units',
                           data='1',
                           status=500)

    self.assertFalse(self.bg.add_units('xpto', 2))

  def test_run_command_should_return_true_on_success(self):
    self.assertTrue(self.bg.run_command('echo test'))

  def test_run_command_should_return_false_on_error(self):
    self.assertFalse(self.bg.run_command('cat undefined_file'))

  def test_run_command_should_return_false_on_undefined_command(self):
    self.assertFalse(self.bg.run_command('undefined_command'))

  def test_run_hook_should_return_true_on_successful_command(self):
    self.assertTrue(self.bg.run_hook('before_pre'))

  def test_run_hook_should_return_false_on_failing_command(self):
    self.assertFalse(self.bg.run_hook('after_swap'))

  def test_run_hook_should_return_true_on_undefined_hook(self):
    self.assertTrue(self.bg.run_hook('after_pre'))

  def mock_total_units(self, values):
    calls = {'count': 0}
    def total_units(*args, **kwargs):
      result = values[calls['count']]
      calls['count'] += 1
      return result
    return total_units
