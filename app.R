list.of.packages <- c("shiny")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

library(shiny)

ui<-fluidPage(
  titlePanel("Riddel road"),
  sidebarLayout(
    sidebarPanel(
      h2("Progress"),
      p(paste("You are at stage","the shortcut code to this stage is:")),
      code('XHAEI')),
    mainPanel(
      h1("Fake coins"),
      p("One of the coins is fake, how many times do you have to weigh them?"),
      br(),
      numericInput(inputId = "answer1",label = "Choose a number",value = 0),
      actionButton("submit","Definit answer"),
      textOutput("judgement1")
    )
  )
)

server<-function(input,output){
  checkanswer<-eventReactive(input$submit,{
    input$answer1==3
  })
  output$judgement1<-renderText({
    if (checkanswer()){
      "That is correct"
    }else{"That is wrong"}
  })
}

shinyApp(ui=ui,server=server)
