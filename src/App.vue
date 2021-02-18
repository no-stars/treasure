<template>
  <div id="app">
    <div class="container">
      <Main />
    </div>
  </div>
</template>

<script>
import Main from "./components/Main.vue"

export default {
  name: "App",

  components: {
    Main
  }
}

</script>

<style lang="sass">
*,
*::before,
*::after
  box-sizing: border-box

body
  margin: 0
  padding: 0
  min-height: 100vh
  line-height: 1.5
  background-color: #FE938C
  text-rendering: optimizeSpeed
  -webkit-font-smoothing: antialiased
  -moz-osx-font-smoothing: grayscale

html
  color: #222
  font-size: 18px
  font-family: monospace
  scroll-behavior: smooth
  -webkit-text-size-adjust: 100%
  -moz-text-size-adjust: 100%
  -webkit-tap-highlight-color: transparent

textarea,
input,
button
  outline: none
  border: none

.container
  width: 100%
  margin: 0 auto
  padding: 0 8px

  @media (min-width: 768px) 
    padding: 40px 0
    width: 750px
  
  @media (min-width: 992px) 
    width: 970px

  @media (min-width: 1200px) 
    width: 1170px


@keyframes float
  0%
    transform: translatey(0px)
  50%
    transform: translatey(-20px)
  100%
    transform: translatey(0px)

@keyframes blink
  0%
    background-color: #FF0000
  100%
    background-color: transparent

</style>
