using ExcelDataReader;
using InsightsAppApi.Data;
using InsightsAppApi.Models.Domain;
using Microsoft.AspNetCore.Mvc;
using System.Data;
using System.Text.Json;

namespace InsightsAppApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class InsightController : ControllerBase
    {
        private readonly ApplicationDbContext _dbContext;
        public InsightController(ApplicationDbContext dbContext)
        {
            _dbContext = dbContext;
        }

        [HttpPost]
        public async Task<IActionResult> Post([FromForm] IFormFile file, [FromForm] string projectName, [FromForm] string dataSource)
        {
            try
            {
                if (file == null || file.Length == 0)
                    return BadRequest("File is empty");

                System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

                using (var stream = new MemoryStream())
                {
                    await file.CopyToAsync(stream);
                    stream.Position = 0;

                    using (var reader = ExcelReaderFactory.CreateReader(stream))
                    {
                        var result = reader.AsDataSet(new ExcelDataSetConfiguration()
                        {
                            ConfigureDataTable = (_) => new ExcelDataTableConfiguration()
                            {
                                UseHeaderRow = true
                            }
                        });

                        var dataEntries = new List<ImportedFeedback>();

                        // Assuming the first table in the Excel file
                        var table = result.Tables[0];
                        var feedbacks = new List<string>();
                        foreach (DataRow row in table.Rows)
                        {
                            var rowData = new Dictionary<string, object>();
                            foreach (DataColumn column in table.Columns)
                            {
                                feedbacks.Add(row[column].ToString());
                            }
                        }

                        var entry = new ImportedFeedback
                        {
                            Id = Guid.NewGuid(),
                            ProjectName = projectName,
                            DataSource = dataSource,
                            FeedbackData = JsonSerializer.Serialize(feedbacks)
                        };

                        await _dbContext.ImportedFeedbacks.AddAsync(entry);
                        await _dbContext.SaveChangesAsync();
                    }
                }

                return Ok("Data processed and saved successfully");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An error occurred: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("BrainDump")]
        public async Task<IActionResult> PostTextData([FromQuery] string questionGuid, [FromBody] TextDataRequest request)
        {
            if (string.IsNullOrEmpty(request.Text))
            {
                return BadRequest("Text cannot be empty.");
            }

            if (string.IsNullOrEmpty(questionGuid))
            {
                return BadRequest("QuestionGuid cannot be empty.");
            }

            var brainDump = new UserInputFeedback
            {
                Id = Guid.NewGuid(),
                QuestionId = Guid.Parse(questionGuid),
                Feedback = request.Text
            };

            await _dbContext.UserInputFeedbacks.AddAsync(brainDump);
            await _dbContext.SaveChangesAsync();
            return Ok(new { Message = "Data saved successfully", Id = questionGuid });
        }

        public class TextDataRequest
        {
            public string Text { get; set; }
        }

    }
}
