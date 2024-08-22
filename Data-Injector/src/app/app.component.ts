import { Component, OnInit } from '@angular/core';
import {
  RouterOutlet,
  RouterLink,
  RouterLinkActive,
  RouterModule,
} from '@angular/router';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DataService } from './data.service';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ReactiveFormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    MatIconModule,
    MatCardModule,
    MatButtonModule,
    MatToolbarModule,
    RouterModule,
    MatFormFieldModule,
    MatSelectModule,
    ReactiveFormsModule,
    NgIf,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  dataForm: FormGroup;
  selectedFile: File | null = null;

  constructor(private fb: FormBuilder, private dataInputService: DataService) {
    this.dataForm = this.fb.group({
      projectName: ['', Validators.required],
      dataSource: ['', Validators.required],
    });
  }

  ngOnInit(): void {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  onSubmit(): void {
    if (this.dataForm.valid) {
      const formData = new FormData();
      formData.append('projectName', this.dataForm.get('projectName')?.value);
      formData.append('dataSource', this.dataForm.get('dataSource')?.value);

      if (this.selectedFile) {
        formData.append('file', this.selectedFile);
      }

      this.dataInputService.submitData(formData).subscribe(
        (response: any) => {
          console.log('Data submitted successfully', response);
          // Handle success (e.g., show a success message)
        },
        (error: any) => {
          console.error('Error submitting data', error);
          // Handle error (e.g., show an error message)
        }
      );
    }
  }
}
