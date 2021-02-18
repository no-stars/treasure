<template>
  <div
    :class="['main', {'error': error}]"
    ref="dropzone"
    @dragover.prevent="handleDragHover"
    @dragleave.prevent="handleDragHover"
    @drop.prevent="handleDrop"
  >
    <div class="logo-treasure">
      <img alt="Vue logo" :src="require(`@/assets/${treasureLogo}`)" />
    </div>

    <div class="workspace locked" v-if="!unlocked">
      <div class="hint" v-if="!requiredPassword">
        Type your secret or <b>drag</b> the file to
        <label ref="label" for="fileselect"
          >upload
          <input
            id="fileselect"
            @change="handleFileSelect"
            ref="file"
            type="file"
            accept=".txt,.treasure"
          />
        </label>
      </div>
      <textarea
        v-model="text"
        v-if="!requiredPassword"
        class="textarea"
        ref="secret"
        cols="30"
        rows="8"
      ></textarea>
      <div class="controllers">
        <input
          v-model="unboxDate"
          v-if="!requiredPassword"
          class="input"
          type="date"
        />
        <input
          v-model="password"
          class="input"
          type="text"
          :placeholder="passwordPlaceholder"
        />
        <button class="btn" @click="handleButton">Submit</button>
      </div>
    </div>
    <div class="workspace unlocked" v-else>
      <pre>{{ textResult }}</pre>
    </div>
  </div>
</template>

<script>
import axios from "axios"

export default {
  data() {
    return {
      text: "",
      password: "",
      unboxDate: 0,
      requiredPassword: false,
      file: null,
      unlocked: false,
      error: false,
      textResult: ""
    }
  },

  computed: {
    unboxTimestamp() {
      return +new Date(this.unboxDate).getTime() / 1000 || 0
    },
    passwordPlaceholder() {
        return this.requiredPassword ? "Password" : "Password (optional)"
    },
    treasureLogo() {
        return this.unlocked ? "unlocked.png" : "locked.png"
    }
  },

  methods: {
    async handleButton() {
      if (this.requiredPassword) {
        this.requestDecrypt(this.password)
      } else {
        const text = await this.requestEncrypt()
        this.downloadTextAsFile(text)
      }
    },

    showError() {
      this.error = true
      setTimeout(() => this.error = false, 500)
    },

    async requestEncrypt() {
      const postData = {
          text: this.text,
          password: this.password,
          timestamp: this.unboxTimestamp
      }

      try {
        const { data } = await axios.post("http://localhost:5000/api/encrypt", postData)
        return data
      } catch (error) {
        this.showError()
      }
    },

    async requestDecrypt(password=null) {
      const formData = new FormData()
      formData.append("file", this.file)
      if (password !== null) {
          formData.append("password", password)
      }
      const headers = {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data'
      }

      try {
        const { data } = await axios.post("http://localhost:5000/api/decrypt", formData, { headers })
        if (data) {
            this.unlocked = true
            this.textResult = data
        }
      } catch (error) {
        if (this.requiredPassword == true) {
          this.showError()
        }
        if (error.response.status === 403) {
            this.requiredPassword = true
        }
      }
    },

    handleFileSelect() {
      const file = this.$refs.file.files[0]
      this.file = file
      this.processFile(file)
    },

    handleDragHover(e) {
      this.$refs.dropzone.className = e.type == "dragover" ? "main hover" : "main"
    },

    processFile(file) {
      this.fileType = this.recognizeFileType(file)
      this.unlocked = false
      switch(this.fileType) {
        case "text":
          this.requiredPassword = false
          this.extractTextFromFile(file)
          break
        case "treasure":
          this.requestDecrypt()
          break
        default:
          this.showError()
          break
        }
    },

    recognizeFileType(file) {
        if (file.type === "text/plain") return "text"
        if (file.name.endsWith(".treasure")) return "treasure"
        return "unknown"
    },

    handleDrop(e) {
      // reset class
      this.handleDragHover(e)
      const files = e.target.files || e.dataTransfer.files
      const file = files[0]
      this.file = file
      if (file === undefined) {
        this.showError()
        return
      }
      this.processFile(file)
    },

    extractTextFromFile(file) {
      const reader = new FileReader()
      reader.readAsText(file)
      reader.onload = () => (this.text = reader.result)
    },

    generateFileName() {
      let blank = 'Unbox me'
      const ext = '.treasure'
      if (this.unboxTimestamp) {
        blank += ` at ${this.unboxDate}`
      }
      if (this.password) {
        blank += ' with password'
      }
      return blank + ext
    },

    downloadTextAsFile(text) {
      const blob = new Blob([text], { type: "text/plain" })
      const link = document.createElement("a")
      link.href = URL.createObjectURL(blob)
      link.download = this.generateFileName()
      // link.download = `Unbox me at ${this.unboxDate}.treasure`
      link.click()
    }
  }
}
</script>

<style lang="sass">
.main
    display: flex
    flex-direction: column
    align-items: center
    border:  3px solid transparent
    &.hover
        border: 3px dashed #222
    &.error
        animation: blink .5s ease-in-out
    .workspace
        width: 100%
        min-height: 200px
        display: flex
        flex-direction: column
        align-items: center
    .logo-treasure
        margin-bottom: 16px
        filter: drop-shadow(8px 12px 22px rgba(0,0,0,.3))
        animation: float 6s ease-in-out infinite
        &>img
            position: relative
            left: 10px
    .hint>label
        text-decoration: underline
        cursor: pointer
        &>input
            display: none
    .textarea
        border-radius: 8px
        margin: 16px 0
        width: 100%
        max-width: 100%
        min-width: 100%
        min-height: 176px
        background-color: #EE837C
        padding: 16px
        font-size: 16px
        @media (min-width: 480px)
            width: 340px
            min-width: 340px

    .controllers
        width: 100%
        margin: 0 auto 20px
        @media (min-width: 480px)
            width: 260px

        .input,
        .btn
            width: 100%
            height: 36px
            border-radius: 4px
            font-size: 16px
            margin-bottom: 16px
            padding: 0 12px
            font-family: monospace
        .input
            background-color: #EE837C
        .btn
            color: #FE938C
            font-weight: bold
            cursor: pointer
            background-color: #222
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)
            transition: box-shadow .3s ease
            &:hover
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)
            &:active
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)

        ::-webkit-input-placeholder
            color: #8c3e3e
        :-ms-input-placeholder
            color: #8c3e3e
        ::-moz-placeholder
            color: #8c3e3e
        :-moz-placeholder
            color: #8c3e3e
</style>