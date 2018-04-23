import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { BASE_PATH } from '../services/variables';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [{provide: BASE_PATH, useValue: 'http://localhost:8080'}, ],
  bootstrap: [AppComponent]
})
export class AppModule { }
