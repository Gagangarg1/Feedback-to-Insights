using InsightsAppApi.Models.Domain;
using Microsoft.EntityFrameworkCore;
using MongoDB.EntityFrameworkCore.Extensions;

namespace InsightsAppApi.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<ImportedFeedback> ImportedFeedbacks { get; set; }
        public DbSet<UserInputFeedback> UserInputFeedbacks { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            modelBuilder.Entity<ImportedFeedback>().ToCollection("ImportedBrainDumps");
            modelBuilder.Entity<UserInputFeedback>().ToCollection("UserInputBrainDump");
        }
    }
}
