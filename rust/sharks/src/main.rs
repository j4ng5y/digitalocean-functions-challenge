use std::collections::HashMap;
use structopt::StructOpt;
use serde_derive::{Deserialize,Serialize};

const API_URL: &str = "https://functionschallenge.digitalocean.com/api/sammy";
const TYPE_VALUES: &[&str] = &[
    "sammy",
    "punk",
    "dinosaur",
    "retro",
    "pizza",
    "robot",
    "pony",
    "bootcamp",
    "xray"
];

#[derive(Debug, Serialize)]
struct Request {
    name: String,

    #[serde(rename(serialize = "type"))]
    _type: String
}

#[derive(Debug, Deserialize)]
struct Response {
    message: String,
    #[serde(default)]
    errors: HashMap<String, Vec<String>>
}

#[derive(StructOpt, Debug)]
#[structopt(name = "sharks", version = "0.1.0")]
struct Opt {
    #[structopt(long = "name")]
    sammy_name: String,

    #[structopt(long = "type", possible_values(TYPE_VALUES))]
    sammy_type: String,
}

fn main() {
    let opt: Opt = Opt::from_args();
    let r: Request = Request {
        name: opt.sammy_name.clone(),
        _type: opt.sammy_type.clone(),
    };
    let c = reqwest::blocking::Client::new();

    let resp_body = serde_json::to_string(&r).unwrap();

    let resp: Response = c.post(API_URL)
        .header("ACCEPT", "application/json")
        .header("CONTENT-TYPE", "application/json")
        .body(resp_body)
        .send()
        .expect("failed to get response")
        .json()
        .expect("failed to get payload");

    if resp.errors.len() > 0 {
        println!("ERROR: {:#?}", resp.errors);
        return
    }
    println!("Successfully created Sammy: {} of type {}", opt.sammy_name, opt.sammy_type)
}
