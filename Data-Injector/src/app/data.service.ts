import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private apiUrl = 'https://localhost:7243/api/Insight'; // Replace with your actual API endpoint

  constructor(private http: HttpClient) {}

  submitData(formData: FormData): Observable<any> {
    return this.http.post(this.apiUrl, formData);
  }
}
