using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Threading.Tasks;

namespace ZeroMQ2
{
    class Program
    {
        static void Main(string[] args)
        {

            var json = new RouteMatrixRequest
            {

                Locations = new[]{
			new Location{
				ID = "Site1",
				Lat = 37.772363,
				Lon = -122.510018
			},
			new Location{
				ID = "Site2",
				Lat = 37.753763,
				Lon = -122.488872
			},
			new Location{
				ID = "Site3",
				Lat = 37.774727,
				Lon = -122.464927
			},
			new Location{
				ID = "Site4",
				Lat = 37.743163,
				Lon = -122.473945
			}
		}
            }.ToJson();

        using (var context = new ZMQ.Context())
            //using (var socket = context.Socket(ZMQ.SocketType.PUSH))
        using (var socket = context.Socket(ZMQ.SocketType.PAIR))
            {
                socket.Connect("tcp://localhost:5559");
                while (true)
                {
                    
                    Console.ReadLine();
                    socket.Send(json, Encoding.UTF8);
                    //byte[] msg = socket.Recv();
                    //string s = Encoding.UTF8.GetString(msg, 0, msg.Length);
                  //  Console.Write(s);
                    TravelDistance[] aryTravelDistance = socket.Recv(UTF8Encoding.UTF8).FromJson<IEnumerable<TravelDistance>>() as TravelDistance[];
                    foreach (TravelDistance td in aryTravelDistance)
                    {
                       // Console.WriteLine(td.Name + "," + td.TravelTime + "," + td.Meters);
                        Console.WriteLine("From: " + td.From + ", To: " + td.To + ", TravelDuration: " + td.TravelDuration + ", Meters: " + td.Miles);
                    }
                  

                }
            }

        }



    }




    //[KnownType(typeof(Location))]
    [DataContract]
    public class TravelDistance
    {

        //public static TravelDistance operator +(TravelDistance first, TravelDistance second)
        //{
        //    if (first == null)
        //    {
        //        first = new TravelDistance();
        //    }
        //    return new TravelDistance()
        //    {
        //        TravelDuration = first.TravelDuration.Add(second.TravelDuration),
        //        Miles = first.Miles + second.Miles
        //    };
        //}


        [DataMember]
        public double TravelDuration { get; set; }

        [DataMember]
        public double Miles { get; set; }

        [DataMember]
        public string From { get; set; }

        [DataMember]
        public string To { get; set; }
    }





    
    // Define other methods and classes here
    [DataContract]
    public class Location : ILocation
    {

        [DataMember]
        public string ID { get; set; }

        [DataMember]
        public double Lat { get; set; }

        [DataMember]
        public double Lon { get; set; }

        public override bool Equals(object obj)
        {
            if (!(obj is ILocation))
            {
                return false;
            }

            var other = obj as ILocation;
            return this.Lat == other.Lat && this.Lon == other.Lon;
        }
    }

    public interface ILocation
    {
        string ID { get; set; }

        double Lat { get; set; }

        double Lon { get; set; }
    }

    [KnownType(typeof(Location))]
    [DataContract]
    public class RouteMatrixRequest
    {
        [DataMember]
        public IEnumerable<ILocation> Locations { get; set; }
        //We might add some some matrix settings here in the future.
    }


    public static class JsonExtensions
    {
        /// <summary>
        /// Deserializes the json string. Note: Make sure that the type you want to deserialize is marked with the DataContract attribute 
        /// failing to do so may cause unexpexted results.
        /// </summary>
        /// <typeparam name="T">The return type.</typeparam>
        /// <param name="json">A json string</param>
        /// <returns>A instance of the given type.</returns>
        public static T FromJson<T>(this string json)
            where T : class
        {
            return new DataContractJsonSerializer(typeof(T)).Deserialize<T>(json);
        }

        public static string ToJson(this object graph)
        {
            return new DataContractJsonSerializer(graph.GetType()).Serialize(graph);
        }

    }

    public static class XmlObjectSerializerExtensions
    {

        public static string Serialize(this XmlObjectSerializer serializer, object graph)
        {
            MemoryStream stream = new MemoryStream();
            serializer.WriteObject(stream, graph);
            stream.Position = 0;
            return new StreamReader(stream).ReadToEnd();
        }

        public static T Deserialize<T>(this XmlObjectSerializer serializer, string json)
            where T : class
        {
            var stream = new MemoryStream(ASCIIEncoding.UTF8.GetBytes(json));
            stream.Position = 0;
            return serializer.ReadObject(stream) as T;
        }
    }

  












}
