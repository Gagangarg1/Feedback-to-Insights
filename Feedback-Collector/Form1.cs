using Newtonsoft.Json;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace FeedbackCollector
{
    public partial class Form1 : Form
    {
        Guid _questionID;
        public Guid QuestionId
        {
            get
            {
                if (_questionID == Guid.Empty)
                {
                    _questionID = Guid.NewGuid();
                    return _questionID;
                }
                return _questionID;
            }
            set
            {
                _questionID = value;
            }
        }

        private readonly HttpClient _client = new HttpClient();
        public Form1()
        {
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private async void button1_ClickAsync(object sender, EventArgs e)
        {
            string inputText = TextBox.Text; // Assume you've added a TextBox for questionGuid
            string apiUrl = $"https://localhost:7243/api/Insight/BrainDump?questionGuid={Uri.EscapeDataString(QuestionId.ToString())}";

            try
            {
                var response = await SendApiRequest(apiUrl, inputText);
                MessageBox.Show($"Your feedback has been submitted successfully", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "API Call Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private async Task<string> SendApiRequest(string url, string inputText)
        {
            var requestData = new { text = inputText };
            var json = JsonConvert.SerializeObject(requestData);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _client.PostAsync(url, content);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        private void RemindLater_Label_Click(object sender, EventArgs e)
        {
            this.Hide();
        }
    }
}
