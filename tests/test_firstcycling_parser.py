"""
Tests for FirstCycling HTML parsing functionality.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import parse_firstcycling_html


class TestFirstCyclingParser(unittest.TestCase):
    """Test cases for the FirstCycling HTML parser."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test HTML content."""
        # This is the actual HTML from the Czech Tour test case
        cls.test_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Czech Tour | FirstCycling</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="The 1st Stage of 2025 Czech Tour was won by Luke Lamperti of Soudal Quick-Step." />
  <meta name="keywords" content="2025 Czech Tour, SAZKA Tour, Czech Cycling Tour, Czech Tour, UCI Race" />
</head>
<body>
<div id='wrapper'>
	<table class="tablesorter sort">
		<thead>
			<tr>
			<th width='3%'>#</th>
			<th>Rider</th>
			<th style="text-align:center;" title="FLAT | Power on the flat (mixed with MTN/MM/HIL on 0-7% slopes)">FLA</th>
			<th style="text-align:center;" title="MOUNTAIN | 30+ min uphill power">MTN</th>
			<th style="text-align:center;" title="MEDIUM MOUNTAIN | ~15 min uphill power">MM</th>
			<th style="text-align:center;" title="HILL | ~5 min uphill power">HIL</th>
			<th style="text-align:center;" title="TIMETRIAL | Flat timetrialing (10-15+ km) ability">TTR</th>
			<th style="text-align:center;" title="PROLOGUE | Short flat timetrialing ability">PRL</th>
			<th style="text-align:center;" title="COBBLES | Skill to ride on cobbles (especially 3* - 5*)">COB</th>
			<th style="text-align:center;" title="SPRINT | Sprintpower & attacks on the flat">SPR</th>
			<th style="text-align:center;" title="ACCELERATION | How fast a rider can accelerate to the maximum power">ACC</th>
			<th style="text-align:center;" title="DOWNHILL | Technical downhill skills">DHI</th>
			<th style="text-align:center;" title="ATTACKING | Attacking frequency">ATT</th>
			<th style="text-align:center;" title="STAMINA | Aerobic efforts at the end of hard races">STA</th>
			<th style="text-align:center;" title="RESISTENCE | Anaerobic efforts at the end of hard races">RES</th>
			<th style="text-align:center;" title="RECUPERATION | Day-to-day energy recovery">REC</th>
			</tr>
		</thead>
		<tbody>
			<tr>
			<td>1 </td>
			<td>
				<span class="flag flag-us"></span>
				<a href="rider.php?r=93695&y=2025" title="Luke Lamperti">
					<span style="text-transform:uppercase;">Lamperti</span> Luke</a>
			</td>
			<td align="center"><span class="pcmBox pcm73">73</span></td>
			</tr><tr>
			<td>2 </td>
			<td>
				<span class="flag flag-it"></span>
				<a href="rider.php?r=191864&y=2025" title="Davide Donati">
					<span style="text-transform:uppercase;">Donati</span> Davide</a>
			</td>
			<td align="center"><span class="pcmBox pcm72">72</span></td>
			</tr><tr>
			<td>3 </td>
			<td>
				<span class="flag flag-ru"></span>
				<a href="rider.php?r=76728&y=2025" title="Gleb Syritsa">
					<span style="text-transform:uppercase;">Syritsa</span> Gleb</a>
			</td>
			<td align="center"><span class="pcmBox pcm73">73</span></td>
			</tr><tr>
			<td>44 </td>
			<td>
				<span class="flag flag-be"></span>
				<a href="rider.php?r=10971&y=2025" title="Yves Lampaert">
					<span style="text-transform:uppercase;">Lampaert</span> Yves</a>
			</td>
			<td align="center"><span class="pcmBox pcm76">76</span></td>
			</tr><tr>
			<td>DNF</td>
			<td>
				<span class="flag flag-au"></span>
				<a href="rider.php?r=222787&y=2025" title="Martin Kapr">
					<span style="text-transform:uppercase;">Kapr</span> Martin</a>
			</td>
			<td align="center"><span class="pcmBox pcm64">64</span></td>
			</tr>		
		</tbody>
	</table>
</div>
</body>
</html>'''

    def test_parse_basic_cyclists(self):
        """Test parsing basic cyclist data from HTML."""
        cyclists, success, error = parse_firstcycling_html(self.test_html)
        
        self.assertTrue(success, f"Parsing should succeed, but got error: {error}")
        self.assertIsNone(error)
        self.assertIsInstance(cyclists, list)
        self.assertEqual(len(cyclists), 5, "Should find exactly 5 cyclists in test HTML")
        
        # Check first cyclist (Luke Lamperti)
        first_cyclist = cyclists[0]
        self.assertEqual(first_cyclist['name'], 'Lamperti Luke')
        self.assertEqual(first_cyclist['rider_id'], '93695')
        self.assertEqual(first_cyclist['href'], 'rider.php?r=93695&y=2025')
        self.assertEqual(first_cyclist['table_row_number'], 1)
        self.assertEqual(first_cyclist['first_cycling_id'], 93695)
        
        # Check second cyclist (Davide Donati)
        second_cyclist = cyclists[1]
        self.assertEqual(second_cyclist['name'], 'Donati Davide')
        self.assertEqual(second_cyclist['rider_id'], '191864')
        self.assertEqual(second_cyclist['href'], 'rider.php?r=191864&y=2025')
        self.assertEqual(second_cyclist['table_row_number'], 2)
        
        # Check last cyclist (Martin Kapr - DNF)
        last_cyclist = cyclists[4]
        self.assertEqual(last_cyclist['name'], 'Kapr Martin')
        self.assertEqual(last_cyclist['rider_id'], '222787')
        self.assertEqual(last_cyclist['table_row_number'], 5)

    def test_parse_cyclist_data_structure(self):
        """Test that each cyclist has the correct data structure."""
        cyclists, success, error = parse_firstcycling_html(self.test_html)
        
        self.assertTrue(success)
        
        for cyclist in cyclists:
            # Check required fields
            self.assertIn('name', cyclist)
            self.assertIn('href', cyclist)
            self.assertIn('rider_id', cyclist)
            self.assertIn('table_row_number', cyclist)
            self.assertIn('first_cycling_id', cyclist)
            
            # Check data types
            self.assertIsInstance(cyclist['name'], str)
            self.assertIsInstance(cyclist['href'], str)
            self.assertIsInstance(cyclist['rider_id'], str)
            self.assertIsInstance(cyclist['table_row_number'], int)
            self.assertIsInstance(cyclist['first_cycling_id'], int)
            
            # Check that name is not empty
            self.assertGreater(len(cyclist['name']), 1)
            
            # Check that href matches expected pattern
            self.assertIn('rider.php?r=', cyclist['href'])
            
            # Check that rider_id is numeric string
            self.assertTrue(cyclist['rider_id'].isdigit())

    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        empty_html = "<html><body></body></html>"
        cyclists, success, error = parse_firstcycling_html(empty_html)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 0)

    def test_parse_html_without_table(self):
        """Test parsing HTML without cyclist table."""
        html_no_table = "<html><body><div>No table here</div></body></html>"
        cyclists, success, error = parse_firstcycling_html(html_no_table)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 0)

    def test_parse_table_without_cyclist_links(self):
        """Test parsing table without cyclist links."""
        html_no_links = '''
        <html><body>
        <table>
            <tr><th>Header</th></tr>
            <tr><td>No links here</td></tr>
        </table>
        </body></html>
        '''
        cyclists, success, error = parse_firstcycling_html(html_no_links)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 0)

    def test_parse_duplicate_cyclists(self):
        """Test that duplicate cyclists are removed."""
        html_with_duplicates = '''
        <html><body>
        <table>
            <tr><th>Header</th></tr>
            <tr>
                <td><a href="rider.php?r=12345&y=2025">Test Rider</a></td>
            </tr>
            <tr>
                <td><a href="rider.php?r=12345&y=2025">Test Rider</a></td>
            </tr>
        </table>
        </body></html>
        '''
        cyclists, success, error = parse_firstcycling_html(html_with_duplicates)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 1, "Duplicate cyclists should be removed")
        self.assertEqual(cyclists[0]['rider_id'], '12345')

    def test_parse_malformed_links(self):
        """Test parsing with malformed or invalid cyclist links."""
        html_malformed = '''
        <html><body>
        <table>
            <tr><th>Header</th></tr>
            <tr>
                <td><a href="rider.php?r=12345&y=2025">Valid Rider</a></td>
            </tr>
            <tr>
                <td><a href="rider.php?not_a_rider=123">Invalid Link</a></td>
            </tr>
            <tr>
                <td><a href="rider.php?r=&y=2025">Empty ID</a></td>
            </tr>
            <tr>
                <td><a href="rider.php?r=67890&y=2025"></a></td>
            </tr>
        </table>
        </body></html>
        '''
        cyclists, success, error = parse_firstcycling_html(html_malformed)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 1, "Only valid cyclist should be parsed")
        self.assertEqual(cyclists[0]['rider_id'], '12345')

    def test_parse_invalid_html(self):
        """Test parsing completely invalid HTML."""
        invalid_html = "This is not HTML at all!"
        cyclists, success, error = parse_firstcycling_html(invalid_html)
        
        self.assertTrue(success)  # BeautifulSoup is very forgiving
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 0)

    def test_parse_bytes_html(self):
        """Test parsing HTML content provided as bytes."""
        html_bytes = self.test_html.encode('utf-8')
        cyclists, success, error = parse_firstcycling_html(html_bytes)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(cyclists), 5)

    def test_cyclist_ids_are_numeric(self):
        """Test that all extracted cyclist IDs are numeric."""
        cyclists, success, error = parse_firstcycling_html(self.test_html)
        
        self.assertTrue(success)
        
        for cyclist in cyclists:
            self.assertTrue(cyclist['rider_id'].isdigit(), 
                          f"Rider ID '{cyclist['rider_id']}' should be numeric")
            self.assertIsInstance(cyclist['first_cycling_id'], int,
                                f"first_cycling_id should be int, got {type(cyclist['first_cycling_id'])}")

    def test_table_row_numbers_are_sequential(self):
        """Test that table row numbers start from 1 and increment."""
        cyclists, success, error = parse_firstcycling_html(self.test_html)
        
        self.assertTrue(success)
        
        # Extract row numbers and check they're sequential starting from 1
        row_numbers = [cyclist['table_row_number'] for cyclist in cyclists]
        expected_rows = [1, 2, 3, 4, 5]  # Based on our test HTML
        self.assertEqual(row_numbers, expected_rows)

    def test_names_are_properly_extracted(self):
        """Test that cyclist names are properly extracted and formatted."""
        cyclists, success, error = parse_firstcycling_html(self.test_html)
        
        self.assertTrue(success)
        
        expected_names = [
            'Lamperti Luke',
            'Donati Davide', 
            'Syritsa Gleb',
            'Lampaert Yves',
            'Kapr Martin'
        ]
        
        actual_names = [cyclist['name'] for cyclist in cyclists]
        self.assertEqual(actual_names, expected_names)


if __name__ == '__main__':
    unittest.main()
