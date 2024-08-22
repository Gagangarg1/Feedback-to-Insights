using System.ComponentModel.DataAnnotations;

namespace InsightsAppApi.Models.Domain
{    public class UserFeedback
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        public string ProjectName { get; set; }

        [Required]
        public string DataSource { get; set; }

        public string FeedbackData { get; set; }
    }
}
