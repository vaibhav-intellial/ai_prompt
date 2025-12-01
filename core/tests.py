from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
from .utils import read_file, compare_data
from unittest.mock import patch, MagicMock

class BOMComparisonTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.compare_url = reverse('core:compare_boms')
        self.result_url = reverse('core:comparison_result')
        self.master_bom_content = b"MPN,Quantity,Reference Designator (Ref Des),Description\nC001,10,C1,Capacitor\nR001,20,R1,Resistor\nU001,1,U1,IC\n"
        self.user_bom_content = b"MPN,Quantity,Reference Designator (Ref Des),Description\nC001,12,C1,Capacitor\nR001,20,R1,Resistor\nD001,5,D1,Diode\n"

    def test_compare_boms_view_get(self):
        """Test the compare_boms view with a GET request"""
        response = self.client.get(self.compare_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_compare_boms_view_post(self):
        """Test the compare_boms view with a POST request"""
        master_file = SimpleUploadedFile("master_bom.csv", self.master_bom_content, content_type="text/csv")
        user_file = SimpleUploadedFile("user_bom.csv", self.user_bom_content, content_type="text/csv")
        
        response = self.client.post(self.compare_url, {
            'master_file': master_file,
            'user_file': user_file,
        })

        self.assertEqual(response.status_code, 302) # Check for redirect
        self.assertRedirects(response, self.result_url)
        
        # Check session data
        self.assertIn('comparison_result', self.client.session)
        comparison_result = self.client.session['comparison_result']
        self.assertEqual(len(comparison_result['added']), 1)
        self.assertEqual(comparison_result['added'][0]['MPN'], 'D001')
        self.assertEqual(len(comparison_result['removed']), 1)
        self.assertEqual(comparison_result['removed'][0]['MPN'], 'U001')
        self.assertEqual(len(comparison_result['modified']), 1)
        self.assertEqual(comparison_result['modified'][0]['MPN'], 'C001')

    def test_comparison_result_view(self):
        """Test the comparison_result view"""
        # First, we need to set up the session data
        session = self.client.session
        session['master_data'] = 'master_data'
        session['user_data'] = 'user_data'
        session['comparison_result'] = 'comparison_result'
        session['master_filename'] = 'master.csv'
        session['user_filename'] = 'user.csv'
        session.save()

        response = self.client.get(self.result_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/result.html')
        self.assertEqual(response.context['master_data'], 'master_data')
        self.assertEqual(response.context['user_data'], 'user_data')
        self.assertEqual(response.context['comparison_result'], 'comparison_result')
        self.assertEqual(response.context['master_filename'], 'master.csv')
        self.assertEqual(response.context['user_filename'], 'user.csv')

    def test_read_file_csv(self):
        """Test the read_file function with a CSV file with dirty columns"""
        dirty_bom_content = b" MPN , qty, ref des, desc\nC001,10,C1,Capacitor\n"
        csv_file = SimpleUploadedFile("dirty_bom.csv", dirty_bom_content, content_type="text/csv")
        df = read_file(csv_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (1, 4))
        self.assertListEqual(list(df.columns), ['MPN', 'Quantity', 'Reference Designator (Ref Des)', 'Description'])


    def test_read_file_with_different_column_names(self):
        """Test the read_file function with different column names"""
        different_column_content = b"Identified MPN,Qty,Reference Designators,Description\nC001,10,C1,Capacitor\n"
        csv_file = SimpleUploadedFile("different_bom.csv", different_column_content, content_type="text/csv")
        df = read_file(csv_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (1, 4))
        self.assertListEqual(list(df.columns), ['MPN', 'Quantity', 'Reference Designator (Ref Des)', 'Description'])

    @patch('core.utils.pdfplumber.open')
    def test_read_file_pdf(self, mock_pdfplumber_open):
        """Test the read_file function with a PDF file"""
        # Create a mock pdf object
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Define the table to be returned by extract_tables
        table = [
            ['Reference designators', 'Quantity', 'Identified MPN', 'Description'],
            ['A1', '1', 'PRO-OB-440', 'Onboard SMD 2400 MHz Antenna for BLE, WLAN/Wifi']
        ]
        mock_page.extract_tables.return_value = [table]

        with open('bom_samples/bom.pdf', 'rb') as f:
            pdf_file = SimpleUploadedFile("bom.pdf", f.read(), content_type="application/pdf")
        
        df = read_file(pdf_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(df.shape[0], 0)
        self.assertIn('MPN', df.columns)
        self.assertIn('Quantity', df.columns)
        self.assertIn('Reference Designator (Ref Des)', df.columns)
        self.assertIn('Description', df.columns)

    def test_compare_data(self):
        """Test the compare_data function"""
        master_df = pd.DataFrame({
            'MPN': ['C001', 'R001', 'U001'],
            'Quantity': [10, 20, 1],
            'Reference Designator (Ref Des)': ['C1', 'R1', 'U1'],
            'Description': ['Capacitor', 'Resistor', 'IC']
        })
        user_df = pd.DataFrame({
            'MPN': ['C001', 'R001', 'D001'],
            'Quantity': [12, 20, 5],
            'Reference Designator (Ref Des)': ['C1', 'R1', 'D1'],
            'Description': ['Capacitor', 'Resistor', 'Diode']
        })

        comparison_result = compare_data(master_df, user_df)

        self.assertEqual(len(comparison_result['added']), 1)
        self.assertEqual(comparison_result['added'][0]['MPN'], 'D001')
        self.assertEqual(len(comparison_result['removed']), 1)
        self.assertEqual(comparison_result['removed'][0]['MPN'], 'U001')
        self.assertEqual(len(comparison_result['modified']), 1)
        self.assertEqual(comparison_result['modified'][0]['MPN'], 'C001')
