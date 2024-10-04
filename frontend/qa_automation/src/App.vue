<template>
  <v-app>
    <v-container fluid>
      <header>
        <h1>Welcome to Our Website</h1>
      </header>
      <main>
        <div>
         <v-row class="d-flex align-baseline justify-center">
          <v-file-input
            label="File input"
            prepend-icon="mdi-camera"
            variant="filled"
            :v-model="file"
            @change="handleFileChange"
          ></v-file-input>
          <v-btn color="primary" @click="uploadFile" :disabled="!file" class="ml-3">
            Upload File
          </v-btn>
         </v-row>
        </div>
        <vuetify-audio
          :file="this.file"
          :v-model="this.file"
          color="primary"
          autoPlay
          downloadable></vuetify-audio>
      </main>
    </v-container>
  </v-app>
</template>
<script>
// import VuetifyAudio from 'vuetify3-audio-player';
import VuetifyAudio from "vuetify3-audio-player";
export default {
  components: {
    VuetifyAudio,
  },
  // data: () => ({
  //   file: "http://www.hochmuth.com/mp3/Boccherini_Concerto_478-1.mp3",
  // }),
  name: 'App',
  data() {
    return {
      file: null,  // This is where the selected file will be stored
    };
  },
  methods: {
    handleFileChange(event) {
      // Access the selected file from the input event
      this.file = event.target.files[0];  // Update the file property
      console.log('File selected:', this.file);
    },
    uploadFile() {
  if (this.file) {
    const formData = new FormData()
    formData.append('file', this.file)

    const questions = [
      {text: "Did the advisor open the call properly?"}
    ]

    // Append each question as a separate form field
   formData.append('questions',JSON.stringify(questions))

    fetch("http://localhost:8000/evaluate-call/", {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Success:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });

    console.log('Uploading file:', this.file);
  } else {
    console.log('No file selected.');
  }
},
  },
};
</script>
<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  min-height: 100vh;
}
.v-application {
  min-height: 100vh; /* Full height of the viewport */
}
header {
  background-color: #1E4B7E;
  padding: 10px;
}
footer {
  background-color: #1E4B7E;
  text-align: center;
  padding: 10px;
}
main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>