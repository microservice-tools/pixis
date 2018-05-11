import { Component, OnInit } from '@angular/core';
import { PetService } from '../services/api/pet.service';
import { Pet } from '../services/model/Pet';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [PetService]
})
export class AppComponent implements OnInit {
  title = 'app';

  constructor(private petService: PetService) {

  }

  public ngOnInit() {
    this.petService.getPetById(0)
      .subscribe(
        (response) => {
          console.log('getPetById(0) response');
          console.log(response);
        },
        (err) => {
          console.log('getPetById(0) error');
          console.log(err);
        }
      );
  }
}
