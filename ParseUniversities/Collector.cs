using System;
using System.Collections.Generic;
using System.Text;
using AngleSharp;
using AngleSharp.Dom;
using System.Linq;
using System.Runtime.CompilerServices;

namespace ConsoleApp1
{
    static class Collector
    {
        static IConfiguration config;

        public static List<string> CollectRegionsLinks(IConfiguration config_, string startAddres)
        {
            config = config_;
            var document = BrowsingContext.New(config).OpenAsync(startAddres);
            var parsedHtml = document.Result;

            List<string> regionAddresses = new List<string>();

            //Select table with all regions in Russia
            var table = parsedHtml.QuerySelectorAll(@"table");
            IElement regionsTable = null;
            foreach (var t in table)
                if (t.Id == "tregion")
                    regionsTable = t;


            //Select links inside regions
            var allRegions = regionsTable.QuerySelectorAll(@"p");
            List<IElement> regions = new List<IElement>();
            foreach (var r in allRegions)
                if (r.ClassName == "MsoListParagraph")
                    regions.Add(r);

            //Fill links of regoins
            foreach (var r in regions)
                regionAddresses.Add("http://indicators.miccedu.ru/monitoring/2019/" + r.QuerySelector(@"a").Attributes["href"].Value);

            GC.Collect();

            return regionAddresses;
        }

        public static List<string> CollectUniversitylinks(List<string> regionsList)
        {
            List<string> UniversityLinksList = new List<string>();

            List<IDocument> parsedHtmls = new List<IDocument>();
            foreach(var region in regionsList)
                parsedHtmls.Add(BrowsingContext.New(config).OpenAsync(region).Result);

            //collecting table witch contains unniversities info pages
            IHtmlCollection<IElement> table = null;
            List<IElement> unisTables = new List<IElement>();
            foreach (var parsedHtml in parsedHtmls)
            {
                table = parsedHtml.QuerySelectorAll(@"table");
                foreach (var t in table)
                    if (t.ClassName == "an")
                        unisTables.Add(t);
            }

            Console.WriteLine("2.1 step...");
            table = null;

            //collecting links to pages with info about universities
            IHtmlCollection<IElement> allUnis = null;
            List<IElement> Unis = new List<IElement>();
            foreach (var unisTable in unisTables)
            {
                allUnis = unisTable.QuerySelectorAll(@"td");
                foreach (var u in allUnis)
                    if (u.ClassName == "inst")
                        Unis.Add(u);
            }
            Console.WriteLine("2.2 step...");
            allUnis = null;

            List<string> UniInfoList = new List<string>();
            foreach (var u in Unis)
                UniInfoList.Add("http://indicators.miccedu.ru/monitoring/2019/_vpo/" + u.QuerySelector(@"a").Attributes["href"].Value);
            Console.WriteLine("2.3 step...");
            Unis = null;

            //............................MUST BE REWORKED............................................

            //List<IDocument> parsedPages = new List<IDocument>();
            //foreach (var page in UniInfoList)
            //    parsedPages.Add(BrowsingContext.New(config).OpenAsync(page).Result);
            //Console.WriteLine("2.4 step...");
            //UniInfoList = null;

            //IHtmlCollection<IElement> allTds = null;
            //IElement tt = null;
            //foreach (var page in parsedPages)
            //{
            //    table = page.QuerySelectorAll(@"table");
            //    foreach (var t in table)
            //        if (t.Id == "info")
            //            tt = t;
            //    allTds = tt.QuerySelectorAll(@"td");
            //    foreach (var a in allTds)
            //        Console.WriteLine(a);
            //}

            return UniversityLinksList;
        }
    }
}
