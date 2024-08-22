using System.ComponentModel.DataAnnotations;

namespace InsightsAppApi.Models.Domain
{
    public class UserInputFeedback
    {
        [Key]

        public Guid Id { get; set; }

        public Guid QuestionId { get; set; }

        [Required]
        public string Feedback { get; set; }
    }
}
