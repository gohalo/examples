package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

type lang struct {
	name    string
	quality float64
}

type byQuality []lang

func (a byQuality) Len() int           { return len(a) }
func (a byQuality) Less(i, j int) bool { return a[i].quality > a[j].quality }
func (a byQuality) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }

func header() {
	header := "en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7"
	val := strings.Split(header, ",")
	langs := make([]lang, 0, len(val))
	for _, v := range val {
		fields := strings.SplitN(v, ";", 2)
		if len(fields) == 1 {
			langs = append(langs, lang{
				name:    fields[0],
				quality: 1.0,
			})
		} else if len(fields) == 2 {
			if f, err := strconv.ParseFloat(fields[1][2:], 64); err == nil {
				langs = append(langs, lang{
					name:    fields[0],
					quality: f,
				})
			}
		}
	}
	sort.Sort(byQuality(langs))
	fmt.Println(langs)
}
