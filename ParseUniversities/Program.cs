using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using AngleSharp;
using AngleSharp.Dom;
using AngleSharp.Html.Dom;
using AngleSharp.Html.Parser;

namespace ConsoleApp1
{
    class Program
    {
        static void Main(string[] args)
        {
            var config = Configuration.Default.WithDefaultLoader();
            var address = "http://indicators.miccedu.ru/monitoring/2019/index.php?m=vpo";
            List<string> regionsLinks = Collector.CollectRegionsLinks(config, address);
            Console.WriteLine("first step...");
            List<string> universitiesLinks = Collector.CollectUniversitylinks(regionsLinks);
        }
    }
}
