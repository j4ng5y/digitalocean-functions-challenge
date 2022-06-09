package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
)

var (
	sammyname string
	sammytype string
)

const (
	API_URL = "https://functionschallenge.digitalocean.com/api/sammy"

	sammyType_Sammy    sammyType = "sammy"
	sammyType_Punk     sammyType = "punk"
	sammyType_Dinosaur sammyType = "dinosaur"
	sammyType_Retro    sammyType = "retro"
	sammyType_Pizza    sammyType = "pizza"
	sammyType_Robot    sammyType = "robot"
	sammyType_Pony     sammyType = "pony"
	sammyType_Bootcamp sammyType = "bootcamp"
	sammyType_XRay     sammyType = "xray"
)

type (
	sammyType string

	sharksRequest struct {
		Name string    `json:"name"`
		Type sammyType `json:"type"`
	}
	sharksResponse struct {
		Message string              `json:"message"`
		Errors  map[string][]string `json:"errors"`
	}
)

func NewSammyType(s string) sammyType {
	var t sammyType

	switch strings.ToLower(s) {
	case "punk":
		t = sammyType_Punk
	case "dinosaur":
		t = sammyType_Dinosaur
	case "retro":
		t = sammyType_Retro
	case "pizza":
		t = sammyType_Pizza
	case "robot":
		t = sammyType_Robot
	case "pony":
		t = sammyType_Pony
	case "bootcamp":
		t = sammyType_Bootcamp
	case "xray":
		t = sammyType_XRay
	default:
		t = sammyType_Sammy
	}

	return t
}

func (t sammyType) String() string {
	return string(t)
}

func (req *sharksRequest) marshalJSON() ([]byte, error) {
	return json.Marshal(req)
}

func (resp *sharksResponse) unmarshalJSON(body io.ReadCloser) error {
	b, err := ioutil.ReadAll(body)
	if err != nil {
		return fmt.Errorf("unable to read body: %w", err)
	}

	return json.Unmarshal(b, resp)
}

func (req *sharksRequest) SetName(name string) *sharksRequest {
	req.Name = name
	return req
}
func (req *sharksRequest) SetType(t sammyType) *sharksRequest {
	req.Type = t
	return req
}

func init() {
	flag.StringVar(&sammyname, "name", "", "The name to give to your new Sammy.")
	flag.StringVar(&sammytype, "type", "", "The type to give to your new Sammy.")
	flag.Parse()

	if sammyname == "" {
		log.Fatal("Sammy has to have a name")
	}
	if sammytype == "" {
		log.Fatal("Sammy has to have a type")
	}
}

func main() {
	var (
		c = http.DefaultClient
		r = &sharksRequest{
			Name: sammyname,
		}
		R = &sharksResponse{}
	)

	r.SetType(NewSammyType(sammytype))

	rb, err := r.marshalJSON()
	if err != nil {
		log.Fatal(err)
	}

	req, err := http.NewRequest(http.MethodPost, API_URL, bytes.NewBuffer(rb))
	if err != nil {
		log.Fatal(err)
	}

	req.Header = map[string][]string{
		"Accept":       []string{"application/json"},
		"Content-Type": []string{"application/json"},
	}

	resp, err := c.Do(req)
	if err != nil {
		log.Fatal(err)
	}

	defer resp.Body.Close()

	if err := R.unmarshalJSON(resp.Body); err != nil {
		log.Fatal(err)
	}

	if len(R.Errors) > 0 {
		log.Fatalf("An error occurred: Message: %s, Errors: %v", R.Message, R.Errors)
	}
	log.Println(R.Message)
}
